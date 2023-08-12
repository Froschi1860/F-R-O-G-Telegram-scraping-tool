import pytz
import telethon
import traceback
from datetime import datetime, timedelta
from frog.backend.core.interface_classes.ScrapeHandler import ScrapeHandler
from frog.backend.core.interface_classes.ErrorLog import write_error_log

DEFAULT_CFG = {
    "offset_id": 0,
    "offset_date": None,  # Excluding specified date
    "add_offset": 0,
    "limit": 100,  # Number of messages scraped in each iteration
    "total_count_limit": 0,  # If last iteration reached this number of messages scraping stops
    "max_id": 0,  # Up to id x-1 are scraped
    "min_id": 0,  # Up to id x are skipped
    "hash": 0,
}

DEFAULT_META = {
    "refs": [],
    "last_msg_id": 0,
    "accessible": True,
    "last_access": "",
}

# This is how many channels will be scraped before the sleep/pause + pause time (adjust if necessary but be mindful and respect Telegram API resources)
TIMEZONE = "Europe/Berlin"


async def channel_exists(client: telethon.TelegramClient, channel_id: int) -> bool:
    channel_exists = True
    try:
        peer = await client.get_input_entity(channel_id)
        if not type(peer) == telethon.types.InputPeerChannel:
            write_error_log("NotAChannel", f"Peer {channel_id} is not channel")
            raise ValueError
    except ValueError:
        channel_exists = False
        write_error_log(
            "Channel does not exist", f"Channel with id {channel_id} does not exist"
        )
    except telethon.errors.UsernameInvalidError:
        channel_exists = False
        write_error_log(
            "UsernameInvalidError",
            f"Invalid username entered. Reference/ID = {channel_id}",
        )
    except Exception:
        channel_exists = False
        write_error_log("Unknown", traceback.format_exc())
    return channel_exists


def get_channel_users(messages: dict) -> list:
    user_ids = set()
    for msg in messages.values():
        if msg["from_id"] != None:
            user_ids.add(msg["from_id"]["user_id"])
    return list(user_ids)


async def scrape_channel(
    client: telethon.TelegramClient,
    cfg: dict,
    scrape_handler: ScrapeHandler,
    phone: str,
) -> dict:
    channel = await client.get_entity(scrape_handler.cur_id(phone))
    all_messages = {}
    total_messages = 0
    offset_id = cfg["offset_id"]
    total_count_limit = cfg["total_count_limit"]
    if cfg["offset_date"] != None:
        end_date = cfg["offset_date"] + timedelta(days=1)
    else:
        end_date = cfg["offset_date"]

    while True:
        if scrape_handler.abort_scraper(phone):
            scrape_handler.reset_abort_scraper(phone)
            break
        messages = await client.get_messages(
            entity=channel,
            limit=cfg["limit"],
            offset_date=end_date,
            offset_id=offset_id,
            max_id=cfg["max_id"],
            min_id=cfg["min_id"],
            add_offset=cfg["add_offset"],
        )
        if len(messages) == 0:
            break
        for message in messages:
            msg_id = message.id
            message_as_dict = message.to_dict()
            message_as_dict["date"] = (
                message_as_dict["date"].astimezone(pytz.timezone(TIMEZONE)).isoformat()
            )
            if (
                cfg["start_date"] != None
                and datetime.fromisoformat(message_as_dict["date"]).date()
                < cfg["start_date"]
            ):
                return all_messages
            all_messages[msg_id] = message_as_dict
        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    return all_messages
