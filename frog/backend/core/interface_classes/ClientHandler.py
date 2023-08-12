import os
import threading
import traceback
import telethon

from frog.backend.core.paths import auth_dir
from frog.backend.core.interface_classes.ErrorLog import write_error_log
from frog.backend.core.interface_classes.Credentials import (
    Credentials,
    update_credentials_flood_wait,
    query_credentials,
)


class ClientHandler:
    def __init__(self, phone_numbers: list) -> None:
        self._active_client = {}
        self._authorized = {}
        for phone in phone_numbers:
            self._active_client[phone] = False
            self._authorized[phone] = False
        self._verification_code = 0
        self._client_ready = threading.Event()
        self._verification_code_neccesary = threading.Event()
        self._verification_code_entered = threading.Event()
        self._wrong_verification_code = threading.Event()
        self._error_on_auth = False
        self._invalid_phone = False
        self._invalid_api_id = False

    def add_phone_number(self, phone_number: str):
        self._active_client[phone_number] = False
        self._authorized[phone_number] = False

    def remove_phone_number(self, phone_number: str):
        self._active_client.pop(phone_number)
        self._authorized.pop(phone_number)

    def is_ready_for_scraping(self, cred: Credentials) -> bool:
        return (
            not self._active_client[cred.phone()]
            and self._authorized[cred.phone()]
            and not cred.flood_wait_active()
        )

    def all_numbers_unable_to_scrape(self, all_credentials: list()) -> bool:
        for cred in all_credentials:
            if self._authorized[cred.phone()] and not cred.flood_wait_active():
                return False
        return True

    def active_client(self, phone: str):
        return self._active_client[phone]

    def set_active_client(self, phone: str):
        self._active_client[phone] = True

    def reset_active_client(self, phone: str):
        self._active_client[phone] = False

    def authorized(self, phone: str | None = None) -> bool | dict:
        if phone == None:
            return self._authorized.copy()
        return self._authorized[phone]

    def set_authorized(self, phone: str) -> None:
        self._authorized[phone] = True

    def reset_authorized(self, phone: str) -> None:
        self._authorized[phone] = False

    def verification_code(self):
        return self._verification_code

    def set_verification_code(self, verification_code):
        self._verification_code = verification_code
        return

    def client_ready(self):
        return self._client_ready

    def verification_code_neccesary(self):
        return self._verification_code_neccesary

    def verification_code_entered(self):
        return self._verification_code_entered

    def wrong_verification_code(self):
        return self._wrong_verification_code

    def error_on_auth(self):
        return self._error_on_auth

    def set_error_on_auth(self):
        self._error_on_auth = True

    def clear_error_on_auth(self):
        self._error_on_auth = False

    def invalid_phone(self):
        return self._invalid_phone

    def set_invalid_phone(self):
        self._invalid_phone = True

    def clear_invalid_phone(self):
        self._invalid_phone = False

    def invalid_api_id(self):
        return self._invalid_api_id

    def set_invalid_api_id(self):
        self._invalid_api_id = True

    def clear_invalid_api_id(self):
        self._invalid_api_id = False


def create_client(credentials: dict):
    phone = credentials["phone"]
    api_id = credentials["api_id"]
    api_hash = credentials["api_hash"]
    session = os.path.join(auth_dir, phone + ".session")
    return telethon.TelegramClient(
        session,
        api_id,
        api_hash,
        connection_retries=1,
        auto_reconnect=False,
    )


async def authorize_client(
    credentials: dict, client_handler: ClientHandler, code_callback
):
    phone = credentials["phone"]
    cred = query_credentials(phone)
    if cred.flood_wait_active():
        client_handler.set_error_on_auth()
        return None
    client = create_client(credentials)
    try:
        client = await client.start(
            phone,
            code_callback=lambda: code_callback(client_handler),
            max_attempts=1,
        )
        client_handler.set_active_client(phone)
        client_handler.set_authorized(phone)
        return client
    except RuntimeError as e:  # Invalid verification code
        client_handler.wrong_verification_code().set()
        client_handler.client_ready().clear()
        await client.log_out()
        write_error_log(
            "Invalid authorization code", f"Invalid authorization code entered."
        )
    except telethon.errors.rpcerrorlist.PhoneNumberInvalidError:
        client_handler.set_error_on_auth()
        client_handler.set_invalid_phone()
        client_handler.client_ready().clear()
        await client.log_out()
        write_error_log(
            "PhoneNumberInvalidError", "Invalid phone number on authorization."
        )
    except telethon.errors.rpcerrorlist.ApiIdInvalidError:
        client_handler.set_error_on_auth()
        client_handler.set_invalid_api_id()
        client_handler.client_ready().clear()
        await client.log_out()
        write_error_log("ApiIdInvalidError", "Invalid API hash or ID on authorization.")
    except telethon.errors.FloodWaitError as e:
        cred = query_credentials(phone)
        cred.add_flood_wait(e.seconds)
        update_credentials_flood_wait(cred)
        write_error_log(
            "FloodWaitError",
            f"Flood wait error for {phone}: {e.seconds} seconds. Aborting client.",
        )
        client_handler.set_error_on_auth()
        client_handler.client_ready().clear()
    except Exception:
        client_handler.set_error_on_auth()
        client_handler.client_ready().clear()
        write_error_log("Unknown", traceback.format_exc())
        await client.log_out()
    return None


async def start_client(credentials: dict, client_handler: ClientHandler):
    phone = credentials["phone"]
    cred = query_credentials(phone)
    if not client_handler.is_ready_for_scraping(cred):
        return None
    try:
        client = await create_client(credentials).start(phone, max_attempts=1)
        client_handler.set_active_client(phone)
        return client
    except telethon.errors.FloodWaitError as e:
        cred.add_flood_wait(e.seconds)
        update_credentials_flood_wait(cred)
        write_error_log(
            "FloodWaitError",
            f"Flood wait error for {phone}. Aborting client.",
        )
    except Exception:
        write_error_log("Unknown", traceback.format_exc())
    return None


async def disconnect_client(
    credentials: dict, client: telethon.TelegramClient, client_handler: ClientHandler
):
    if client_handler.active_client(credentials["phone"]):
        await client.disconnect()
        client_handler.reset_active_client(credentials["phone"])
