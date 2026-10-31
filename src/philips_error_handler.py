class PhilipsDownloaderError(Exception):
    """Base class for exceptions in this module"""
    pass


class PhilipsDatabaseError(PhilipsDownloaderError):
    """Exception raised for database errors in the Philips downloader."""
    def __init__(self, message):
        self.message = message


class PhilipsTryAgainError(PhilipsDownloaderError):
    """Exception raised for temporal errors in the Philips downloader."""
    def __init__(self, message):
        self.message = message


class PhilipsNoPatientFoundError(PhilipsDownloaderError):
    """Exception raised for Not found patient errors in the Philips downloader."""
    def __init__(self, message):
        self.message = message


class PhilipsBreakError(PhilipsDownloaderError):
    """Exception raised to break loops in the Philips downloader."""
    def __init__(self, message):
        self.message = message


class PhilipsCancelError(PhilipsDownloaderError):
    """Exception raised to cancel operations in the Philips downloader."""
    def __init__(self, message):
        self.message = message


class PhilipsStopError(PhilipsDownloaderError):
    """Exception raised to stop operations in the Philips downloader."""
    def __init__(self, message):
        self.message = message


class PhilipsAbortError(PhilipsDownloaderError):
    """Exception raised to abort operations in the Philips downloader."""
    def __init__(self, message):
        self.message = message


class PhilipsNoDataError(PhilipsDownloaderError):
    """Exception raised for no data errors in the Philips downloader."""
    def __init__(self, message):
        self.message = message


class PhilipsElementNotFoundError(PhilipsDownloaderError):
    """Exception raised for elemet not found errors in the Philips downloader."""
    def __init__(self, message):
            self.message = message
