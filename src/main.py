import os
import sys

from philips_document_downloader import PhilipsDocumentDownloader
from database_namager import PhilipsDatabaseManager
from excel_manager import PhilipsExcelManager

from constants import PORTAL_USER, PORTAL_PASSWORD
from constants import PAGES
from constants import DATABASE_NAME
from constants import EXCEL_FILE_NAME


ACTUAL_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(ACTUAL_DIR, DATABASE_NAME)
EXCEL_FILE = os.path.join(ACTUAL_DIR, EXCEL_FILE_NAME)


def fill_database(database_manager: PhilipsDatabaseManager, row_init: int, row_end: int):
    excel_manager =  PhilipsExcelManager(database_manager, EXCEL_FILE)
    excel_manager.get_list(row_init, row_end)


def create_philips_patients_report(database_manager: PhilipsDatabaseManager):
    excel_manager = PhilipsExcelManager(database_manager)
    excel_manager.create_philips_patients_report()


def create_philips_names_report(database_manager: PhilipsDatabaseManager):
    excel_manager = PhilipsExcelManager(database_manager)
    excel_manager.create_philips_names_report()


def download_documents(database_manager: PhilipsDatabaseManager):
    pdd = PhilipsDocumentDownloader(database_manager)
    pdd.navegate(PAGES.LOGIN.value, PORTAL_USER, PORTAL_PASSWORD)

if __name__ == "__main__":
    database_manager = PhilipsDatabaseManager(DB_FILE)
    if len(sys.argv) > 1:
        if sys.argv[1] == "fill_db":
            fill_database(database_manager, int(sys.argv[2]), int(sys.argv[3]))
        elif sys.argv[1] == "patients_report":
            create_philips_patients_report(database_manager)
        elif sys.argv[1] == "names_report":
            create_philips_names_report(database_manager)
    else:
        download_documents(database_manager)
