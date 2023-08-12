import asyncio

from frog.backend.core.interface_classes.ClientHandler import (
    ClientHandler,
    disconnect_client,
    authorize_client,
)


def run_verification_thread(client_handler: ClientHandler, credentials: dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_verification_session(client_handler, credentials))
    loop.close()


async def start_verification_session(client_handler: ClientHandler, credentials: dict):
    client = await authorize_client(
        credentials, client_handler, prompt_verification_code_input
    )
    if client != None:
        client_handler.client_ready().set()
        await disconnect_client(credentials, client, client_handler)


def prompt_verification_code_input(client_handler: ClientHandler):
    client_handler.verification_code_neccesary().set()
    if client_handler.error_on_auth():
        return 0
    client_handler.verification_code_entered().wait(120)
    if not client_handler.verification_code_entered().is_set():
        return 0
    client_handler.verification_code_entered().clear()
    return client_handler.verification_code()
