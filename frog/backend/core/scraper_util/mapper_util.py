import time
import telethon
import traceback
from frog.backend.core.interface_classes.NameIdMap import (
    NameIdMap,
    query_name_id_mapping,
    save_name_id_mapping,
)
from frog.backend.core.interface_classes.Channel import (
    query_meta_data,
    save_meta_data,
    ChannelMeta,
)
from frog.backend.core.interface_classes.ErrorLog import write_error_log
from . import channel_exists


async def map_ref_to_id(client: telethon.TelegramClient, channel_ref: str) -> int:
    if await channel_exists(client, channel_ref):
        channel_id = None
        try:
            channel_id = await retrieve_channel_id(client, channel_ref)
        except telethon.errors.ChannelPrivateError:
            write_error_log(
                "ChannelPrivateError", f"The channel {channel_ref} is private."
            )
            return -1
        except Exception:
            write_error_log("Unknown", traceback.format_exc())
            return -1
        name_id_map = query_name_id_mapping(channel_ref)
        if name_id_map == None:
            save_name_id_mapping(NameIdMap(channel_ref, channel_id))
        meta = query_meta_data(channel_id)
        if meta == None:
            meta = ChannelMeta()
        meta.set_last_access(time.localtime())
        if channel_ref not in meta.refs():
            meta.add_ref(channel_ref)
        save_meta_data(channel_id, meta)
        return channel_id
    return -1  # Channel does not exist


async def map_id_to_refs(client: telethon.TelegramClient, channel_id: int) -> list:
    if await channel_exists(client, channel_id):
        out = []
        meta = query_meta_data(channel_id)
        try:
            ref = await retrieve_channel_name(client, channel_id)
            if meta == None:
                save_name_id_mapping(NameIdMap(ref, channel_id))
                meta = ChannelMeta()
            meta.set_accessible()
            if ref not in meta.refs():
                save_name_id_mapping(NameIdMap(ref, channel_id))
                meta.add_ref(ref)
            out.append(ref)
        except telethon.errors.ChannelPrivateError:
            write_error_log(
                "ChannelPrivateError", f"The channel with id {channel_id} is private."
            )
            meta.reset_accessible()
        except Exception:
            write_error_log("Unknown", traceback.format_exc())
        meta.set_last_access(time.localtime())
        save_meta_data(channel_id, meta)
        return out
    return None  # Channel does not exist


async def retrieve_channel_id(
    client: telethon.TelegramClient, channel_link: str
) -> int:
    channel = await client.get_input_entity(channel_link)
    return channel.to_dict()["channel_id"]


async def retrieve_channel_name(client: telethon.TelegramClient, channel_id: int):
    channel = await client.get_entity(channel_id)
    return channel.to_dict()["username"]
