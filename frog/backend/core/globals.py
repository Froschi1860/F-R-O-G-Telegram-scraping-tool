from .interface_classes.ClientHandler import ClientHandler
from .interface_classes.Credentials import query_all_phone_numbers
from .interface_classes.ScrapeHandler import ScrapeHandler


class AppContext:
    def __init__(self) -> None:
        self._instance_is_running = False

    def instance_is_running(self) -> bool:
        return self._instance_is_running

    def set_instance_is_running(self):
        self._instance_is_running = True


# Globals
context = AppContext()
phone_numbers = query_all_phone_numbers()
client_handler = ClientHandler(phone_numbers)
scrape_handler = ScrapeHandler(phone_numbers)
