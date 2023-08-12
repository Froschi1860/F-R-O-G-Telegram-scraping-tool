from datetime import datetime

from tinydb import where
from frog.backend.core.db import db_error_log, error_db_lock

FLOOD_WAIT_ABORT_THRESHOLD = 120


def backend_log(text: str):
    with open("backend_log.txt", "a", encoding="utf-8") as f:
        print(text, file=f)


class ErrorLog:
    def __init__(self, type: str, message: str) -> None:
        self._timestamp = datetime.now().isoformat()
        self._type = type
        self._message = message

    def to_dict(self) -> dict:
        return {
            "timestamp": self._timestamp,
            "type": self._type,
            "message": self._message,
        }


def save_error_in_db(error: ErrorLog) -> int:
    with error_db_lock:
        return db_error_log.insert(error.to_dict())


def write_error_log(error_type: str, message: str) -> None:
    save_error_in_db(ErrorLog(error_type, message))


def query_error_log():
    with error_db_lock:
        errors = db_error_log.all()
        errors.reverse()
        return errors


def delete_error_log():
    with error_db_lock:
        db_error_log.truncate()
