import pandas as pd

from database_namager import PhilipsDatabaseManager
from logger import philips_logger

class PhilipsExcelManager:

    def __init__(self, database_manager: PhilipsDatabaseManager, excel_filepath: str |None = None):
        self.database_manager = database_manager
        self.excel_filepath = excel_filepath

    def create_philips_patients_report(self):
        with self.database_manager as db:
            df = pd.read_sql("SELECT * FROM patients", db.conn)
            df.to_excel("philips_patients_report.xlsx", index=False)
            philips_logger.info(f"📄 Philips Patients Report file created")

    def create_philips_names_report(self):
        with self.database_manager as db:
            df = pd.read_sql("SELECT * FROM names", db.conn)
            df.to_excel("philips_names_report.xlsx", index=False)
            philips_logger.info(f"📄 Philips Names Report file created")

    def get_excel_data(self, init_row: int, end_row: int, columns: list):
        philips_logger.info(f"📄 Getting the excel data from row {init_row} to {end_row}")
        rows_to_skip = init_row - 1
        total_rows_to_read = (end_row - init_row) + 1

        df = pd.read_excel(
            self.excel_filepath,
            skiprows=range(1, rows_to_skip),
            nrows=total_rows_to_read,
            usecols=columns,
            converters={
                "report_initial_date": str,
                "report_final_date": str
            }
        )

        if "report_initial_date" in df.columns:
            df["report_initial_date"] = pd.to_datetime(df["report_initial_date"]).dt.strftime('%m/%d/%Y')
        if "report_final_date" in df.columns:
            df["report_final_date"] = pd.to_datetime(df["report_final_date"]).dt.strftime('%m/%d/%Y')

        return df

    def get_list(self, init: int, end: int):
        philips_logger.info(f"📄 Reading Excel file: {self.excel_filepath}")
        interested_columns = ["id", "patient_name", "document_number", "report_initial_date","report_final_date", "file_name"]
        result = self.get_excel_data(init, end, interested_columns)
        dictionaries_list = result.to_dict(orient="records")
        with self.database_manager as db:
            db.save_list(dictionaries_list)
