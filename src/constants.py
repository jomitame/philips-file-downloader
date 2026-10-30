from os import getenv
from enum import Enum

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Web Page
PORTAL_USER = getenv("PORTAL_USER", "")
PORTAL_PASSWORD = getenv("PORTAL_PASSWORD", "")
WEBPAGE = getenv("WEBPAGE", "")

# Connections
DATABASE_NAME = getenv("DATABASE_NAME", "")
EXCEL_FILE_NAME = getenv("EXCEL_FILE_NAME", "")

# Data
MINIMUM_REPORTS_TO_DOWNLOAD = 2

# Selectors TAGS
class SELECTORS(Enum):
    LOGIN_USERNAME_FIELD = "#username"
    LOGIN_PASSWORD_FIELD = "#password"
    LOGIN_BUTTON = "#loginSubmit"
    USAGE_TRAKING_MODAL = ".analytics-modal"
    USER_MENU =  "#pr-primary-navbar-v2-toggle-user-nav"
    #USER_MENU = ".pr-icon.pr-icon-close"
    LOGOUT_OPTION = ".logout"


# sleep pause times
class PAUSES_TIME(Enum):
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
