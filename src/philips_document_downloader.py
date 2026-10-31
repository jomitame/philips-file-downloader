import time

from playwright._impl._errors import TimeoutError
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page, Locator
from playwright_stealth import Stealth

from logger import philips_logger
from constants import SELECTORS, PAUSES_TIME, ERROR_TYPES, PAGES, DB_ERROR_NUMBERS, MINIMUM_REPORTS_TO_DOWNLOAD
from database_namager import PhilipsDatabaseManager
from philips_error_handler import PhilipsAbortError, PhilipsTryAgainError, PhilipsCancelError, PhilipsStopError, PhilipsElementNotFoundError
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
            raise PhilipsElementNotFoundError(f"No se pudo encontrar {field_name} con selector: {field_selector}")
        except Exception as e:
            raise PhilipsCancelError(f"Canceling process")

    def click_element(self, page: Page, element_name: str, element_selector: str, timeout: int = 45000):
        """Hace click en un elemento de la pagina (enlace o boton)"""
        try:
            philips_logger.info(f"⏳ Waiting for {element_name} ...")
            page.wait_for_selector(element_selector, timeout=timeout)
            philips_logger.info(f"🕵️ {element_name} detected.")
            philips_logger.info(f"🖱️ Clicking to {element_name}")
            page.click(element_selector)
            time.sleep(PAUSES_TIME.SHORT.value)
        except TimeoutError as e:
            raise PhilipsElementNotFoundError(f"No se pudo encontrar {element_name} con selector: {element_selector}")
        except Exception as e:
            raise PhilipsCancelError(f"Canceling process")

    def click_by_role_and_name(self, page: Page, element_role: str, element_name:str):
        """Hace click en un elemento por el rol y nombre"""
        try:
            philips_logger.info(f"⏳ Waiting for {element_name} ...")
            page.get_by_role(element_role, name=element_name).click()
            time.sleep(PAUSES_TIME.QUICK.value)
            philips_logger.info(f"🕵️ {element_name} detected.")
            philips_logger.info(f"🖱️ Clicking to {element_name}")
            time.sleep(PAUSES_TIME.SHORT.value)
        except TimeoutError as e:
            raise PhilipsElementNotFoundError(f"No se pudo encontrar {element_name} con rol: {element_role}")
        except Exception as e:
            raise PhilipsCancelError(f"Canceling process")

    def click_group_element(self, page: Page, element_name: str, group_selector: str, position: int):
        """Hace click en un elemento de un grupo de elementos"""
        try:
            philips_logger.info(f"⏳ Waiting for {element_name} ...")
            page.wait_for_selector(group_selector, timeout=45000)
            philips_logger.info(f"🕵️ {element_name} detected.")
            philips_logger.info(f"🖱️ Clicking to {element_name}")
            page.locator(group_selector).nth(position).click()
            time.sleep(PAUSES_TIME.QUICK.value)
        except TimeoutError as e:
            raise PhilipsElementNotFoundError(f"No se pudo encontrar {element_name} con selector: {group_selector} y posicion {position}")
        except Exception as e:
            raise PhilipsCancelError(f"Canceling process")

    def write_login_username(self, page: Page, user:str):
        """Escribe el usuario en el formulario de login"""
        try:
            self.write_field(page, "login username field", SELECTORS.LOGIN_USERNAME_FIELD.value, user)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al escribir el nombre de usuario en login")
            raise PhilipsStopError(f"Stoping login writing username process")

    def write_login_password(self, page: Page, password:str):
        """Escribe el usuario en el formulario de login"""
        try:
            self.write_field(page, "login password field", SELECTORS.LOGIN_PASSWORD_FIELD.value, password)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al escribir el password en login")
            raise PhilipsStopError(f"Stoping login writing password process")

    def click_to_login_button(self, page: Page):
        """Hace click en el boton de login para loguearse"""
        try:
            self.click_element(page, "login button", SELECTORS.LOGIN_BUTTON.value)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
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
        except (PhilipsStopError, PhilipsElementNotFoundError) as e:
            raise PhilipsAbortError (f"Aborting process: {e}")

    def logout(self, page):
        """Hace logout en el sitio web de Philips"""
        philips_logger.info("🏁 Process completed.")
        time.sleep(PAUSES_TIME.SHORT.value)
        self.click_element(page, "user menu", SELECTORS.USER_MENU.value)
        time.sleep(PAUSES_TIME.SHORT.value)
        self.click_element(page, "logout option", SELECTORS.LOGOUT_OPTION.value)

    def evaluate_document_search_cleaner(self, page: Page):
        """Evalua si aparece el limpador de campo y le da click"""
        cleaner_showed = page.locator(SELECTORS.DOCUMENT_SEARCH_CLEANER.value).count() > 0
        if cleaner_showed:
            philips_logger.info("Limpiando campo de busqueda de documento.")
            self.click_element(page, "document search cleaner", SELECTORS.DOCUMENT_SEARCH_CLEANER.value)
            time.sleep(PAUSES_TIME.SHORT.value)

    def click_to_id_externo(self, page: Page):
        """Hace click en el boton ID externo (External ID) para buscar por documento"""
        try:
            self.click_group_element(page, "External ID Button", SELECTORS.EXTERNAL_ID.value, 3)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al intentar hacer click en boton de ID externo")
            raise PhilipsTryAgainError(f"Try againg later")

    def write_patient_document_number(self, page: Page, document_number: str):
        """Escribe el numero de documento en el campo de texto"""
        try:
            self.write_field(page, "Document search field", SELECTORS.DOCUMENT_SEARCH_FIELD.value, document_number)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al intentar escribir el numero de documento del paciente en el campo de busqueda")
            raise PhilipsTryAgainError(f"Try againg later")

    def go_to_patients_page(self, page: Page):
        """Refresca la pagina"""
        philips_logger.info("Heading to the patient's page")
        #page.reload()
        page.goto(PAGES.PATIENTS.value)

    def click_to_search_patients(self, page: Page):
        """Hace click en la lupa del campo de busqueda"""
        try:
            self.click_element(page, "Search document button", SELECTORS.DOCUMENT_SEARCH_FINDER.value)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al dar click en buscador de documento del paciente en el campo de busqueda")
            raise PhilipsTryAgainError(f"Try againg later.")

    def save_multiples_names(self, dicci_list:list):
        """Guarda en base de datos los distintos nombres que arrojo la busqueda para el documento"""
        try:
            with self.database_manager as db:
                db.save_names(dicci_list)
        except PhilipsDatabaseError as e:
            raise PhilipsAbortError(f"Aborting process: {e}")

    def get_patients_result(self, page: Page, record_id: int) -> Locator:
            """Obtiene los pacientes del resultado de la busqueda"""
            philips_logger.info("Geting patients search result")
            results = page.locator(SELECTORS.NAME_CARD_SEARCH_RESULT.value)
            return results

    def try_to_click_patient(self, page: Page, record_id: int):
        """Intenta dar click al paciente si existe"""
        results = self.get_patients_result(page, record_id)
        results_quantity = results.count()
        #TODO: descomentar
        #self.update_database_record_with_quantity_names(record_id, results_quantity)
        if results_quantity < 1:
            raise PhilipsNoPatientFoundError("No patients for this document number")
        elif results_quantity > 1:
            names_items = results.all()
            dicci_list = [{'record_id':record_id, 'name': name.inner_text()} for name in names_items]
            #print(dicci_list)
            #TODO: descomentar
            #self.save_multiples_names(dicci_list)
        results.last.click()

    def click_to_timeframe_dropdown(self, page: Page):
        """Hace click en el selector de marco de tiempo para elegir el tipo de informe"""
        try:
            self.click_element(page, "Timeframe dropdown", SELECTORS.TIMEFRAME_DROPDOWN.value, 90000)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al dar click en el selector de marco de tiempo del informe")
            raise PhilipsTryAgainError(f"Try againg later.")

    def click_to_custom_date_range_option(self, page: Page):
        """Hace click en la opcion intervalo de fechas personalizado"""
        try:
            # TODO: pasar texto a constants
            self.click_by_role_and_name(page, "button", "Custom date range")
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al intentar hacer click en Intervalo de fecha perzonalizado")
            raise PhilipsTryAgainError(f"Try againg later")

    def click_to_date_picker_from(self, page: Page):
        """Hace click en el selector de fecha inicial"""
        try:
            self.click_group_element(page, "Date picker from", SELECTORS.DATE_PICKERS.value, 0)
            page.keyboard.press("Control+A")
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al intentar hacer click en el selector de fecha inicial")
            raise PhilipsTryAgainError(f"Try againg later")

    def write_date_from(self, page: Page, initial_date: str):
        """Escribe la fecha inicial del reporte"""
        try:
            first_date_input = page.get_by_test_id("DateInput").first
            first_date_input.fill(initial_date)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al intentar escribir la fecha inicial del reporte")
            raise PhilipsTryAgainError(f"Try againg later")

    def click_to_date_picker_to(self, page: Page):
        """Hace click en el selector de fecha final"""
        try:
            self.click_group_element(page, "Date picker to", SELECTORS.DATE_PICKERS.value, 1)
            page.keyboard.press("Control+A")
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al intentar hacer click en selector de fecha final")
            raise PhilipsTryAgainError(f"Try againg later")
    
    def write_date_to(self, page: Page, final_date: str):
        """Escribe la fecha final del reporte"""
        try:
            last_date_input = page.get_by_test_id("DateInput").last
            last_date_input.fill(final_date)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al intentar escribir la fecha final del reporte")
            raise PhilipsTryAgainError(f"Try againg later")

    def click_to_create_report(self, page):
        """Hace click en el boton crear reporte"""
        try:
            self.click_element(page, "create Report Buton", SELECTORS.CREATE_REPORT_BUTTON.value)
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al dar click en el boton de crear el informe")
            raise PhilipsTryAgainError(f"Try againg later.")

    def download_report(self, page: Page, patient_data: dict):
        """Descarga el reporte"""
        try:
            with page.expect_download() as download_info:
                self.click_group_element(page, "PDF Generator", SELECTORS.GENERATE_PDF_BUTTON.value, 0)
                time.sleep(PAUSES_TIME.LONG.value)
            download = download_info.value
            philips_logger.info("💾 Saving the PDF File.")
            download.save_as(f"reports/{patient_data['file_name']}")
        except (PhilipsElementNotFoundError, PhilipsCancelError):
            philips_logger.error(f"⛔ Error al dar click en el boton de crear el informe")
            raise PhilipsTryAgainError(f"Try againg later.")

    def update_database_record_to_error(self, record_id: int, obs: str, error_number = -1):
        """Actualiza el registro en base de datos y lo setea como error"""
        philips_logger.error(f"❌ Updating the record with ID {record_id} to error in the database.")
        try:
            with self.database_manager as db:
                db.update_record_to_error(record_id, obs, error_number)
        except PhilipsDatabaseError as e:
            raise PhilipsAbortError(f"Aborting process: {e}")

    def update_database_record_with_quantity_names(self, record_id: int, quantity:int):
        """Actualiza el registro en base de datos con la cantidad de nombres encontrados"""
        philips_logger.info(f"Updating quantity of name links for record with ID {record_id} to {quantity} in the database.")
        try:
            with self.database_manager as db:
                db.update_record_quantity_names(record_id, quantity)
        except PhilipsDatabaseError as e:
            philips_logger.error(f"⛔ Error updating quantity of name links: {e}")
        except Exception as e:
            philips_logger.error(f"⛔ Unexpected error updating quantity of name links: {e}")
            raise PhilipsAbortError(f"Unexpected error updating quantity of name links: {e}")

    def loop_through_records(self, page: Page, patients_to_look_for: list):
        """Recorre los registros a descargar"""
        for i, patient in enumerate(patients_to_look_for):
            philips_logger.info(f"--- 🔍 Looking for record with id: {patient['id']} : ({i+1}/{len(patients_to_look_for)}) ---")
            try:
                self.go_to_patients_page(page)
                time.sleep(PAUSES_TIME.LONG.value)
                
                self.evaluate_traking_modal(page)
                self.click_to_id_externo(page)
                self.write_patient_document_number(page, patient['document_number'])
                self.click_to_search_patients(page)
                time.sleep(PAUSES_TIME.LONG.value)
                self.try_to_click_patient(page, patient['id'])
                self.click_to_timeframe_dropdown(page)
                self.click_to_custom_date_range_option(page)
                self.click_to_date_picker_from(page)
                self.write_date_from(page, patient['report_initial_date'])
                self.click_to_date_picker_to(page)
                self.write_date_to(page, patient['report_final_date'])
                self.click_to_create_report(page)
                self.download_report(page, patient)
                #self.evaluate_document_search_cleaner(page)
                
            except PhilipsTryAgainError as e:
                philips_logger.error(f"⛔ TryAgainError: {e}. Skipping record with document number: {patient['document_number']}")
                #self.update_database_record_to_error(record["id"], f"{ERROR_TYPES.TRY_AGAIN.value}: {e}", DB_ERROR_NUMBERS.get(ERROR_TYPES.TRY_AGAIN, ERROR_TYPES.DEFAULT.value))
                continue
            except PhilipsNoPatientFoundError as e:
                philips_logger.error(f"⛔ PatientNotFoundError: {e}. Skipping record with document number: {patient['document_number']}")
                #self.update_database_record_to_error(record["id"], f"{ERROR_TYPES.NO_PATIENT.value}: {e}", DB_ERROR_NUMBERS.get(ERROR_TYPES.NO_PATIENT, ERROR_TYPES.DEFAULT.value))
                continue
            except PhilipsNoDataError as e:
                pass
            except (PhilipsCancelError, PhilipsBreakError) as e:
                philips_logger.error
                raise PhilipsAbortError (f"Aborting process: {e}")
            except PhilipsDatabaseError as e:
                philips_logger.error
                raise PhilipsAbortError (f"Aborting process: {e}")
        
    def navegate(self, url: str, user: str, password: str):
        patients_to_look_for = self.get_list_to_look_for()
        with Stealth().use_sync(sync_playwright()) as p:
            try:
                self.launch_headless_browser(p)
                page = self.connect_to_page()
                self.open_philips_website(page, url)
                self.login(page, user, password)
                time.sleep(PAUSES_TIME.SHORT.value)
                self.loop_through_records(page, patients_to_look_for)
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
