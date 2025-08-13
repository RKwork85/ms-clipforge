from pydantic import BaseModel
from datetime import datetime

class FileRecord(BaseModel):
    filename: str
    path: str
    upload_time: str
    class_name: str
    upload_type: str
    username: str
    size: float
