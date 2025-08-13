from app.models.file_record import FileRecord
from app.utils.logger import logger

file_records = []

def add_file_record(file_record: FileRecord):
    file_records.append(file_record)

def get_all_file_records():
    return file_records
