import threading
import asyncio
import time
import traceback
import queue
import telethon
from telethon.errors import ChannelPrivateError
from frog.backend.core.interface_classes.Channel import (
    save_msgs,
    ChannelMeta,
    query_meta_data,
    save_meta_data,
)
from frog.backend.core.interface_classes.ErrorLog import (
    write_error_log,
    FLOOD_WAIT_ABORT_THRESHOLD,
)
from frog.backend.core.interface_classes.Credentials import (
    query_all_credentials,
    update_credentials_flood_wait,
)


from frog.backend.core.interface_classes.ClientHandler import (
    ClientHandler,
    start_client,
    disconnect_client,
)
from frog.backend.core.interface_classes.ScrapeHandler import ScrapeHandler
from frog.backend.core.scraper_util import get_channel_users, scrape_channel
from frog.backend.core.scraper_util.mapper_util import map_ref_to_id
from frog.backend.core.interface_classes.Credentials import Credentials


def start_scraper_thread(
    scrape_handler: ScrapeHandler,
    client_handler: ClientHandler,
    credentials: Credentials,
) -> str:
    scraper_thread = threading.Thread(
        target=run_scraper_thread,
        args=[scrape_handler, client_handler, credentials],
    )
    scraper_thread.start()
    return scraper_thread.name


def run_scraper_thread(
    scrape_handler: ScrapeHandler,
    client_handler: ClientHandler,
    credentials: Credentials,
) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        scrape_multiple_channels(scrape_handler, client_handler, credentials)
    )
    loop.close()


## Create an intermediary function that maps ref to id and consumes queue to call scrape_single_channel
async def scrape_multiple_channels(
    scrape_handler: ScrapeHandler,
    client_handler: ClientHandler,
    credentials: Credentials,
) -> None:
    phone = credentials.as_dict()["phone"]
    scrape_handler.set_active_scraper(phone)
    while True:
        if client_handler.all_numbers_unable_to_scrape(query_all_credentials()):
            scrape_handler.scraper_done(phone)
            scrape_handler.reset_queue()
            return
        channel_id = 0
        try:
            client = await start_client(credentials.as_dict(), client_handler)
            if client == None:
                scrape_handler.scraper_queue().join()
                scrape_handler.scraper_done(phone)
                return
            ref = scrape_handler.scraper_queue().get(False)

            channel_id = await map_ref_to_id(client, ref)
            await disconnect_client(credentials.as_dict(), client, client_handler)

        except queue.Empty:
            await disconnect_client(credentials.as_dict(), client, client_handler)
            break
        if channel_id == -1:
            if not scrape_handler.user_queue_reset():
                scrape_handler.scraper_queue().task_done()
            continue
        scrape_handler.set_cur_id(channel_id, phone)
        await scrape_single_channel(scrape_handler, client_handler, credentials)
        scrape_handler.set_last_scraped(channel_id, phone)
        if not scrape_handler.user_queue_reset():
            scrape_handler.scraper_queue().task_done()

    scrape_handler.scraper_done(phone)
    scrape_handler.scraper_queue().join()
    scrape_handler.reset_queue()


async def scrape_single_channel(
    scrape_handler: ScrapeHandler,
    client_handler: ClientHandler,
    credentials: Credentials,
) -> None:
    phone = credentials.as_dict()["phone"]
    channel_id = scrape_handler.cur_id(phone)
    meta = query_meta_data(channel_id)
    if meta == None:
        meta = ChannelMeta()
    cfg = scrape_handler.cfg()
    if not cfg["force_full"]:
        cfg["min_id"] = meta.last_msg_id()
    client = await start_client(credentials.as_dict(), client_handler)
    if client == None:
        return
    try:
        msgs = await scrape_channel(client, cfg, scrape_handler, phone)
        channel_users = get_channel_users(msgs)
        meta.update_channel_users(channel_users)
        msgs = include_type_in_msg_headers(msgs)
        save_msgs(channel_id, msgs)
        meta.set_last_access(time.localtime())
        meta.set_accessible()
        if len(msgs) > 0:
            meta.set_last_msg_id(int(max(msgs.keys())))
    except ChannelPrivateError:
        write_error_log(
            "ChannelPrivateError", f"The channel with id {channel_id} is private."
        )
        meta.reset_accessible()
        scrape_handler.set_error_on_scrape()
    except telethon.errors.FloodWaitError as e:
        scrape_handler.set_error_on_scrape()
        credentials.add_flood_wait(e.seconds)
        update_credentials_flood_wait(credentials)

        if e.seconds > FLOOD_WAIT_ABORT_THRESHOLD:
            write_error_log(
                "FloodWaitError",
                f"Flood wait error for {phone}. Wait is higher then threshold. Aborting scraper.",
            )
        else:
            write_error_log(
                "FloodWaitError",
                f"Flood wait error for {phone}. Waiting {e.seconds * 2} seconds to continue with next channel.",
            )
            await asyncio.sleep(e.seconds * 2)
    except Exception:
        write_error_log("Unknown", traceback.format_exc())
        scrape_handler.set_error_on_scrape()
    save_meta_data(channel_id, meta)
    await disconnect_client(credentials.as_dict(), client, client_handler)


def include_type_in_msg_headers(msgs: dict) -> dict:
    """Replaces "_" in message keys with "type" """
    out = dict()
    for key, value in msgs.items():
        if type(value) == dict:
            out[key] = include_type_in_msg_headers(value)
            continue
        if key == "_":
            key = "type"
        out[key] = value
    return out
