from os import getenv
from enum import Enum

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Web Page
PORTAL_USER = getenv("PORTAL_USER", "")
PORTAL_PASSWORD = getenv("PORTAL_PASSWORD", "")

# Connections
DATABASE_NAME = getenv("DATABASE_NAME", "")
EXCEL_FILE_NAME = getenv("EXCEL_FILE_NAME", "")

# Data
MINIMUM_REPORTS_TO_DOWNLOAD = 10

# Pages
class PAGES(Enum):
    LOGIN = "https://www.careorchestrator.com/#/login"
    PATIENTS = "https://www.careorchestrator.com/#/patient/search"

# Selectors TAGS
class SELECTORS(Enum):
    LOGIN_USERNAME_FIELD = "#username"
    LOGIN_PASSWORD_FIELD = "#password"
    LOGIN_BUTTON = "#loginSubmit"
    USAGE_TRAKING_MODAL = ".analytics-modal"
    USER_MENU =  "#pr-primary-navbar-v2-toggle-user-nav"
    LOGOUT_OPTION = ".logout"
    EXTERNAL_ID = ".has-label.icon-left.pr-btn"
    DOCUMENT_SEARCH_CLEANER = ".pr-btn-clear.pr-btn-alt.has-icon.icon-left.pr-btn.pr-btn-quiet.pr-search-btn-reset.pr-fade-show.pr-fade-hide"
    DOCUMENT_SEARCH_FIELD = ".form-control.search-term.ng-pristine.ng-valid.ng-star-inserted.ng-touched"
    DOCUMENT_SEARCH_FINDER = ".search-term-input-group-btn.lh-sm"
    NAME_CARD_SEARCH_RESULT = ".pr-result-title.pr-result-title-link"
    TIMEFRAME_DROPDOWN = ".ng-untouched.ng-pristine.ng-valid.ng-star-inserted"
    DATE_PICKERS = ".input-group.input-group-inline"
    CREATE_REPORT_BUTTON = ".pr-btn-createReportBtn.pr-btn-undefined.has-label.icon-left.pr-btn"
    GENERATE_PDF_BUTTON = ".has-icon.icon-left.pr-btn.pr-btn-link"


# sleep pause times
class PAUSES_TIME(Enum):
    QUICK = 1
    SHORT = 2
    MEDIUM = 4
    LONG = 6


# Error
class ERROR_TYPES(Enum):
    DEFAULT = -1
    TRY_AGAIN = "Try again later"
    NO_DATA = "No data"
    NO_PATIENT = "No patients listed"
    STOP = "Stop error"
    DATA_BASE = "Database error"
    UNSPECTED = "Unspected error"

DB_ERROR_NUMBERS = {
    ERROR_TYPES.TRY_AGAIN : -2,
    ERROR_TYPES.NO_DATA: -3,
    ERROR_TYPES.NO_PATIENT : -4,
    ERROR_TYPES.STOP: -5,
    ERROR_TYPES.DATA_BASE: -6,
    ERROR_TYPES.UNSPECTED: -7
}
