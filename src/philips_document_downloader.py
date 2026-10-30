import time

from playwright._impl._errors import TimeoutError
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page
from playwright_stealth import Stealth

from logger import philips_logger
from constants import SELECTORS, PAUSES_TIME, ERROR_TYPES, DB_ERROR_NUMBERS, MINIMUM_REPORTS_TO_DOWNLOAD
from database_namager import PhilipsDatabaseManager
from philips_error_handler import PhilipsAbortError, PhilipsTryAgainError, PhilipsCancelError, PhilipsStopError
from philips_error_handler import PhilipsNoPatientFoundError, PhilipsNoDataError, PhilipsBreakError, PhilipsDatabaseError


class PhilipsDocumentDownloader:

    def __init__(self, database_manager: PhilipsDatabaseManager):
        self.database_manager = database_manager
        self.browser: Browser | None = None
        self.browser_context: BrowserContext | None = None

    def get_list_to_look_for(self) -> list:
        """Busca en base de datos y crea una lista de dicccionarios con los registros que no se han descargado"""
        philips_logger.info("📋 Getting the list of records to look for in the database.")
        with self.database_manager as db:
            maxi_number_of_records = db.get_quantity_not_downloaded_records()[0]
            limited_records = db.get_limited_not_downloaded_records(min(MINIMUM_REPORTS_TO_DOWNLOAD, maxi_number_of_records))
            records = [dict(row) for row in limited_records]
        return records

    def launch_headless_browser(self, p: Playwright, silence: bool = True) -> None:
        """Abre el navegador en modo silencioso si silence es True"""
        philips_logger.info("📄 Launching Headless Chromium browser with Stealth ...")
        self.browser = p.chromium.launch(headless=silence)

    def connect_to_page(self) -> Page:
        """Se conecta a la pagina del navegador"""
        if not self.browser:
            raise RuntimeError("Navegador NO iniciado.")
        self.browser_context = self.browser.new_context()
        return self.browser_context.new_page()

    def open_philips_website(self, page: Page, url: str):
        """Visita el sitio web de Philips: careorchestrator"""
        philips_logger.info("📖 Opening Philips webpage ...")
        page.goto(url)
        time.sleep(PAUSES_TIME.LONG.value)

    def write_field(self, page: Page, field_name: str, field_selector: str, value:str):
        """Escribe en un campo de texto"""
        try:
            philips_logger.info(f"⏳ Waiting for {field_name} ...")
            page.wait_for_selector(field_selector, timeout=45000)
            philips_logger.info(f"🕵️ {field_name} detected.")
            philips_logger.info(f"✍️ Writing {field_name}...")
            page.fill(field_selector, value)
            time.sleep(PAUSES_TIME.SHORT.value)
        except TimeoutError as e:
            raise PhilipsTryAgainError(f"No se pudo encontrar {field_name} con selector: {field_selector}")
        except Exception as e:
            raise PhilipsCancelError(f"Canceling process")

    def click_element(self, page: Page, element_name: str, element_selector: str):
        """Hace click en un elemento de la pagina (enlace o boton)"""
        try:
            philips_logger.info(f"⏳ Waiting for {element_name} ...")
            page.wait_for_selector(element_selector, timeout=45000)
            philips_logger.info(f"🕵️ {element_name} detected.")
            philips_logger.info(f"🖱️ Clicking to {element_name}")
            page.click(element_selector)
            time.sleep(PAUSES_TIME.SHORT.value)
        except TimeoutError as e:
            raise PhilipsTryAgainError(f"No se pudo encontrar {element_name} con selector: {element_selector}")
        except Exception as e:
            raise PhilipsCancelError(f"Canceling process")

    #TODO: Escribir el selector tag del campo en constants
    def write_login_username(self, page: Page, user:str):
        """Escribe el usuario en el formulario de login"""
        try:
            self.write_field(page, "login username field", SELECTORS.LOGIN_USERNAME_FIELD.value, user)
        except (PhilipsTryAgainError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al escribir el nombre de usuario en login")
            raise PhilipsStopError(f"Stoping login writing username process")

    def write_login_password(self, page: Page, password:str):
            """Escribe el usuario en el formulario de login"""
            try:
                self.write_field(page, "login password field", SELECTORS.LOGIN_PASSWORD_FIELD.value, password)
            except (PhilipsTryAgainError, PhilipsCancelError):
                philips_logger.error(f"⛔ Error al escribir el password en login")
                raise PhilipsStopError(f"Stoping login writing password process")

    def click_to_login_button(self, page: Page):
        """Hace click en el boton de login para loguearse"""
        try:
            self.click_element(page, "login button", SELECTORS.LOGIN_BUTTON.value)
        except (PhilipsTryAgainError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al hacer click en boton de login")
            raise PhilipsStopError(f"Stoping login button click process")

    def evaluate_traking_modal(self, page: Page):
        """Evalua si aparece un modal de seguimiento"""
        modal_showed = page.locator(SELECTORS.USAGE_TRAKING_MODAL.value).count() > 0
        if modal_showed:
            philips_logger.info("Modal de seguimiento mostrado.")
            self.click_element(page, "modal tracking", SELECTORS.USAGE_TRAKING_MODAL.value)
            time.sleep(PAUSES_TIME.SHORT.value)
            #page.wait_for_timeout(500)
            page.keyboard.press("Tab")
            time.sleep(PAUSES_TIME.SHORT.value)
            page.keyboard.press("Tab")
            time.sleep(PAUSES_TIME.SHORT.value)
            page.keyboard.press("Enter")
            time.sleep(PAUSES_TIME.SHORT.value)

    def login(self, page: Page, user: str, password: str):
        """Hace login en el sitio web de Philips"""
        try:
            self.write_login_username(page, user)
            self.write_login_password(page, password)
            self.click_to_login_button(page)
            self.evaluate_traking_modal(page)
        except PhilipsStopError as e:
            raise PhilipsAbortError (f"Aborting process: {e}")

    def logout(self, page):
        """Hace logout en el sitio web de Philips"""
        philips_logger.info("🏁 Process completed.")
        time.sleep(PAUSES_TIME.SHORT.value)
        self.click_element(page, "user menu", SELECTORS.USER_MENU.value)
        time.sleep(PAUSES_TIME.SHORT.value)
        self.click_element(page, "logout option", SELECTORS.LOGOUT_OPTION.value)
        
    def navegate(self, url: str, user: str, password: str):
        records_to_look_for = self.get_list_to_look_for()
        with Stealth().use_sync(sync_playwright()) as p:
            try:
                self.launch_headless_browser(p, False)
                page = self.connect_to_page()
                self.open_philips_website(page, url)
                self.login(page, user, password)
                self.logout(page)
            except RuntimeError as e:
                philips_logger.error(f"⛔ Execution error: {e}")
            except PhilipsAbortError as e:
                philips_logger.error(f"⛔ Abort error: {e}")
            except Exception as e:
                philips_logger.error(f"⛔ Unexpected error: {e}")
            finally:
                philips_logger.info("🚪 Closing browser.")
                if self.browser_context:
                    self.browser_context.close()
                if self.browser:
                    self.browser.close()
