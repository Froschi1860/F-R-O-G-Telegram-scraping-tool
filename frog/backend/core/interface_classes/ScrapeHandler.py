from queue import Queue


class ScrapeHandler:
    """Construct a global object to handle multithreaded scraping."""

    def __init__(self, phone_numbers: list) -> None:
        self._scraper_queue = Queue()  # Contains channel references
        self._user_queue_reset = False  # Avoid errors from calls to task_done
        self._active_scraper = {}
        self._cur_id = {}
        self._last_scraped = {}
        self._abort_scraper = {}
        self._errors_on_scrape = 0
        for phone in phone_numbers:
            self._active_scraper[phone] = False
            self._cur_id[phone] = 0
            self._last_scraped[phone] = 0
            self._abort_scraper[phone] = False
        self._cfg = {
            "offset_id": 0,
            "offset_date": None,  # Excluding specified date
            "start_date": None,  # Including specified date
            "add_offset": 0,
            "limit": 100,  # Number of messages scraped in each iteration
            "total_count_limit": 0,  # If last iteration reached this number of messages scraping stops
            "max_id": 0,  # Up to id x-1 are scraped
            "min_id": 0,  # Up to id x are skipped
            "hash": 0,
            "force_full": False,
        }

    def scraper_queue(self) -> Queue:
        return self._scraper_queue

    def create_scraper_queue(self, channel_refs: list) -> None:
        if not self.scraper_queue().empty():
            raise ValueError
        new_queue = Queue()
        for ref in channel_refs:
            new_queue.put(ref)
        self._scraper_queue = new_queue
        self.reset_user_queue_reset()

    def add_to_queue(self, channel_refs: list) -> None:
        queue = self.scraper_queue()
        for ref in channel_refs:
            queue.put(ref)

    def reset_queue(self) -> None:
        self.set_user_queue_reset()
        self._scraper_queue = Queue()

    def user_queue_reset(self) -> bool:
        return self._user_queue_reset

    def set_user_queue_reset(self) -> None:
        self._user_queue_reset = True

    def reset_user_queue_reset(self) -> None:
        self._user_queue_reset = False

    def add_phone_number(self, phone: str):
        self._active_scraper[phone] = False
        self._cur_id[phone] = 0
        self._last_scraped[phone] = 0
        self._abort_scraper[phone] = False

    def remove_phone_number(self, phone: str) -> None:
        self._active_scraper.pop(phone)
        self._cur_id.pop(phone)
        self._last_scraped.pop(phone)
        self._abort_scraper.pop(phone)

    def active_scraper(self, phone: str) -> bool:
        return self._active_scraper[phone]

    def any_active_scraper(self) -> bool:
        for active in self._active_scraper.values():
            if active:
                return True
        return False

    def any_inactive_scraper(self) -> bool:
        for active in self._active_scraper.values():
            if not active:
                return True
        return False

    def set_active_scraper(self, phone: str) -> None:
        self._active_scraper[phone] = True

    def reset_active_scraper(self, phone: str) -> None:
        self._active_scraper[phone] = False

    def cur_id(self, phone: str) -> int:
        return self._cur_id[phone]

    def set_cur_id(self, channel_id: int, phone: str) -> None:
        self._cur_id[phone] = channel_id

    def reset_cur_id(self, phone: str) -> None:
        self._cur_id[phone] = 0

    def last_scraped(self, phone: str) -> int:
        return self._last_scraped[phone]

    def set_last_scraped(self, last_scraped_id: int, phone: str) -> None:
        self._last_scraped[phone] = last_scraped_id

    def reset_last_scraped(self, phone: str) -> None:
        self._last_scraped[phone] = 0

    def abort_scraper(self, phone: str):
        return self._abort_scraper[phone]

    def set_abort_scraper(self, phone: str):
        self._abort_scraper[phone] = True

    def reset_abort_scraper(self, phone: str):
        self._abort_scraper[phone] = False

    def errors_on_scrape(self) -> int:
        return self._errors_on_scrape

    def set_error_on_scrape(self) -> None:
        self._errors_on_scrape += 1

    def reset_errors_on_scrape(self) -> None:
        self._errors_on_scrape = 0

    def cfg(self) -> dict:
        return self._cfg.copy()

    def set_cfg(self, key: str, value) -> None:
        new_cfg = self._cfg.copy()
        new_cfg[key] = value
        self._cfg = new_cfg.copy()

    def reset_cfg(self) -> None:
        self._cfg = {
            "offset_id": 0,
            "offset_date": None,  # Excluding specified date
            "start_date": None,  # Including specified date
            "add_offset": 0,
            "limit": 100,  # Number of messages scraped in each iteration
            "total_count_limit": 0,  # If last iteration reached this number of messages scraping stops
            "max_id": 0,  # Up to id x-1 are scraped
            "min_id": 0,  # Up to id x are skipped
            "hash": 0,
            "force_full": False,
        }

    def scraper_done(self, phone: str) -> None:
        if self.active_scraper(phone):
            self.set_last_scraped(self.cur_id(phone), phone)
            self.reset_cur_id(phone)
            self.reset_active_scraper(phone)
