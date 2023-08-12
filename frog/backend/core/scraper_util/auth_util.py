import telethon
import traceback

from frog.backend.core.interface_classes.Credentials import Credentials
from frog.backend.core.interface_classes.ClientHandler import (
    ClientHandler,
    create_client,
)
from frog.backend.core.interface_classes.ErrorLog import write_error_log


async def check_auth_for_credentials(
    credentials_list: list, client_handler: ClientHandler
):
    for cred in credentials_list:
        client = None
        try:
            if type(cred) != Credentials:
                raise ValueError
            client = create_client(cred.as_dict())
            await client.connect()
            if await client.is_user_authorized():
                cred.set_authorized()
                client_handler.set_authorized(cred.phone())
            else:
                cred.reset_authorized()
                client_handler.reset_authorized(cred.phone())
            await client.disconnect()
        except Exception:
            write_error_log("Unknown", traceback.format_exc())
            cred.reset_authorized()
            client_handler.reset_authorized(cred.phone())
        await client.disconnect()
