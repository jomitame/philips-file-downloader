import sqlite3

from philips_error_handler import PhilipsDatabaseError


class PhilipsDatabaseManager:

	def __init__(self, filepath: str):
		self.filepath = filepath
		self.conn = None

	def __enter__(self):
		try:
			self.conn = sqlite3.connect(self.filepath)
			self.conn.row_factory = sqlite3.Row
			cursor = self.conn.cursor()
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS patients (
					id INTEGER PRIMARY KEY,
					patient_name TEXT NOT NULL,
					document_number TEXT NOT NULL,
					report_initial_date TEXT NOT NULL,
					report_final_date TEXT NOT NULL,
					file_name TEXT NOT NULL,
                    downloaded INTEGER NOT NULL DEFAULT 0,
                    quantity_names INTEGER NOT NULL DEFAULT 0,
                    observation TEXT NOT NULL DEFAULT ''
				)
			''')
			cursor.execute('''
				CREATE TABLE IF NOT EXISTS names (
					id INTEGER PRIMARY KEY,
					record_id TEXT NOT NULL,
					name TEXT NOT NULL
				)
			''')
			return self
		except sqlite3.Error as e:
			raise PhilipsDatabaseError(f"Database error: {e}")

	def __exit__(self, exc_type, exc_val, exc_tb):
		try:
			if self.conn:
				if exc_type is None:
					self.conn.commit()
				else:
					self.conn.rollback()
		except sqlite3.Error as e:
			raise PhilipsDatabaseError(f"Database error on exit: {e}")
		finally:
			if self.conn:
				self.conn.close()
				self.conn = None

	def save_list(self, data_list: list):
		try:
			cursor = self.conn.cursor()
			query = '''
				INSERT OR IGNORE INTO patients (
					id, patient_name, document_number, report_initial_date, report_final_date, file_name
				)
				VALUES (?, ?, ?, ?, ?, ?)
			'''
			values = [
				(
					dicci["id"], dicci["patient_name"],dicci["document_number"],
					dicci["report_initial_date"],dicci["report_final_date"],dicci["file_name"]
				)
				for dicci in data_list
			]
			cursor.executemany(query, values)
		except (sqlite3.Error, KeyError) as e:
			raise PhilipsDatabaseError(f"Error guardando la lista en lote {e}")

	def save_name(self, dicci_list: list):
		try:
			cursor = self.conn.cursor()
			query = '''
				INSERT OR IGNORE INTO names (
					recodr_id, name
				)
				VALUES (?, ?)
			'''
			values = [
				(
					dicci["record_id"], dicci["name"]
				)
				for dicci in dicci_list
			]
			cursor.executemany(query, values)
		except (sqlite3, KeyError) as e:
			raise PhilipsDatabaseError(f"Error al guar dar la lista de nombres en lote: {e}")

	def update_record(self, id: int, downloaded: int, obs: str):
		cursor = self.conn.cursor()
		cursor.execute('''
			UPDATE patients
			SET downloaded = ?,
				observation = ?
			WHERE id = ?
		''', (downloaded, obs, id))

	def update_record_to_downloaded(self, id: int):
		self.update_record(id,1,"Ok")

	def update_record_to_error(self, id: int, obs: str, error_number: int):
		self.update_record(id, error_number, obs)

	def update_record_quantity_names(self, id: int, quantity_names: int):
		cursor = self.conn.cursor()
		cursor.execute('''
			UPDATE patients
			SET quantity_names = ?
			WHERE id = ?
		''', (quantity_names, id))

	def get_quantity_not_downloaded_records(self):
		cursor = self.conn.cursor()
		cursor.execute('''
			SELECT COUNT(*)
			FROM patients
			WHERE downloaded = 0 
		''')
		return cursor.fetchone()

	def get_limited_not_downloaded_records(self, quantity_limit: int):
		cursor = self.conn.cursor()
		cursor.execute('''
			SELECT id, patient_name, document_number, report_initial_date, report_final_date, file_name
			FROM patients
			WHERE downloaded = 0
			LIMIT ?
		''', (quantity_limit,))
		return cursor.fetchall()
