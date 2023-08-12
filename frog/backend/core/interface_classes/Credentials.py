from datetime import datetime, timedelta
import traceback
from frog.backend.core.db import db_cred, cred_db_lock
from tinydb.table import Document

from frog.backend.core.interface_classes.ErrorLog import write_error_log


class Credentials:
    def __init__(self) -> None:
        self._username = ""
        self._phone = ""
        self._api_id = ""
        self._api_hash = ""
        self._flood_wait = ""
        self._authorized = False

    def set_credentials(
        self,
        username: str = None,
        phone: str = None,
        api_id: str = None,
        api_hash: str = None,
        flood_wait: str = None,
    ):
        if username != None:
            self._username = username

        if phone != None:
            self._phone = phone

        if api_id != None:
            self._api_id = api_id

        if api_hash != None:
            self._api_hash = api_hash

        if flood_wait != None:
            self._flood_wait = flood_wait

    def phone(self) -> str:
        return self._phone

    def authorized(self) -> bool:
        return self._authorized

    def set_authorized(self):
        self._authorized = True

    def reset_authorized(self):
        self._authorized = False

    def flood_wait_active(self) -> bool:
        self.assert_flood_wait()
        return self._flood_wait != ""

    def assert_flood_wait(self) -> None:
        if self._flood_wait == "":
            return
        if datetime.now() > datetime.fromisoformat(self._flood_wait):
            self._flood_wait = ""
            return

    def add_flood_wait(self, seconds: int):
        if seconds == 0:
            return
        flood_wait_end = datetime.now() + timedelta(seconds=seconds)
        self._flood_wait = flood_wait_end.isoformat()

    def as_dict(self):
        return {
            "username": self._username,
            "phone": self._phone,
            "api_id": self._api_id,
            "api_hash": self._api_hash,
            "flood_wait": self._flood_wait,
            "authorized": self._authorized,
        }

    def complete(self):
        return (
            self._username != ""
            and self._phone != ""
            and self._api_id != ""
            and self._api_hash != ""
        )


def query_credentials(phone: str) -> Credentials:
    try:
        key = int(phone)
        with cred_db_lock:
            cred_from_db = db_cred.get(doc_id=key)
            credentials = Credentials()
            credentials.set_credentials(
                username=cred_from_db["username"],
                phone=cred_from_db["phone"],
                api_id=cred_from_db["api_id"],
                api_hash=cred_from_db["api_hash"],
                flood_wait=cred_from_db["flood_wait"],
            )
        return credentials
    except Exception:
        write_error_log("Unknown", traceback.format_exc())
        return None


def query_all_credentials() -> list:
    out = list()
    all_cred = list()
    with cred_db_lock:
        all_cred = db_cred.all()
    for doc in all_cred:
        cred = Credentials()
        cred.set_credentials(
            username=doc["username"],
            phone=doc["phone"],
            api_id=doc["api_id"],
            api_hash=doc["api_hash"],
            flood_wait=doc["flood_wait"],
        )
        out.append(cred)
    return out


def query_all_phone_numbers() -> list:
    phone_numbers = list()
    cred_from_db = list()
    with cred_db_lock:
        cred_from_db = db_cred.all()
    for cred in cred_from_db:
        phone_numbers.append(cred.get("phone"))
    return phone_numbers


def save_credentials(credentials: Credentials) -> bool:
    try:
        with cred_db_lock:
            doc_id = db_cred.insert(
                Document(credentials.as_dict(), int(credentials.phone()))
            )
        return doc_id == int(credentials.phone())
    except ValueError:
        return False


def update_credentials_flood_wait(credentials: Credentials) -> bool:
    phone = credentials.phone()
    try:
        with cred_db_lock:
            updated = db_cred.update(credentials.as_dict(), doc_ids=[int(phone)])
            return updated[0] == int(phone)
    except (ValueError, KeyError):
        return False


def update_credentials(phone: str, username: str, api_id: str, api_hash: str) -> bool:
    credentials = Credentials()
    credentials.set_credentials(username, phone, api_id, api_hash)
    try:
        with cred_db_lock:
            updated = db_cred.update(credentials.as_dict(), doc_ids=[int(phone)])
            return updated[0] == int(phone)
    except (ValueError, KeyError):
        return False


def delete_credentials(phone: str) -> bool:
    try:
        with cred_db_lock:
            deleted = db_cred.remove(doc_ids=[int(phone)])
            return deleted[0] == int(phone)
    except ValueError:
        return False
