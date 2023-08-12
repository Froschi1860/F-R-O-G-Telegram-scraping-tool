import os
import json
import csv

from frog.backend.core.interface_classes.Channel import (
    query_msgs,
    query_msgs_as_list,
    query_meta_data,
)

from frog.backend.core.interface_classes.NameIdMap import (
    query_all_mappings_sorted_by_ref,
)
from frog.backend.core.interface_classes.ErrorLog import query_error_log

null_value = "NA"
seperator = "_"


def write_meta_to_json(
    output_dir_path: str, channel_id: int, overwrite_existing: bool = False
) -> str:
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError("Output directory does not exist.")
    path = os.path.join(output_dir_path, f"{channel_id}_meta" + ".json")
    if os.path.exists(path) and not overwrite_existing:
        return None
    meta = query_meta_data(channel_id)
    if meta == None:
        raise ValueError("Invalid channel ID.")
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(meta.as_dict(), outfile, ensure_ascii=False, indent=2)
    return output_dir_path


def write_msgs_to_json(
    output_dir_path: str, channel_id: int, overwrite_existing: bool = False
) -> str:
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError("Output directory does not exist.")
    path = os.path.join(output_dir_path, str(channel_id) + ".json")
    if os.path.exists(path) and not overwrite_existing:
        return None
    msgs = query_msgs(channel_id)
    if msgs == None:
        raise ValueError("Invalid channel ID.")
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(msgs, outfile, ensure_ascii=False, indent=2)
    return output_dir_path


def write_msgs_to_csv(
    output_dir_path: str, channel_id: int, overwrite_existing: bool = False
) -> str:
    if not os.path.exists(output_dir_path):
        raise FileNotFoundError("Output directory does not exist.")
    path = os.path.join(output_dir_path, str(channel_id) + ".csv")
    if os.path.exists(path) and not overwrite_existing:
        return None
    msgs = query_msgs_as_list(channel_id)
    if msgs == None:
        raise ValueError("Invalid channel ID.")
    flattened_msgs, channel_keys = flatten_channel(msgs)
    with open(path, "w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=channel_keys, restval=null_value)
        writer.writeheader()
        writer.writerows(flattened_msgs)
    return output_dir_path


def write_name_id_maps_csv(output_dir: str):
    if not os.path.exists(output_dir):
        raise FileNotFoundError("Output directory does not exist.")
    path = os.path.join(output_dir, "name_id_maps.csv")
    name_id_maps = query_all_mappings_sorted_by_ref()
    if len(name_id_maps) == 0:
        return None
    with open(path, "w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["channel_ref", "channel_id"])
        writer.writeheader()
        writer.writerows(name_id_maps)
    return output_dir


def write_error_log_csv(output_dir: str):
    if not os.path.exists(output_dir):
        raise FileNotFoundError("Output directory does not exist.")
    path = os.path.join(output_dir, "error_log.csv")
    errors = query_error_log()
    if len(errors) == 0:
        return None
    with open(path, "w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["timestamp", "type", "message"])
        writer.writeheader()
        writer.writerows(errors)
    return output_dir


def flatten_channel(messages: list):
    flattened_channel = []
    channel_keys = set()

    for message in messages:
        unpacked, msg_keys = flatten_message(message, {})
        flattened_channel.append(unpacked)
        channel_keys = channel_keys.union(msg_keys)

    return flattened_channel, channel_keys.copy()


def flatten_message(
    message: dict,
    unpacked: dict,
    key_prefix: str = "",
    msg_keys: set = None,
):
    if msg_keys == None:
        msg_keys = set()
    for key, value in message.items():
        new_key = f"{key_prefix}{seperator}{key}" if key_prefix else str(key)
        if type(value) == dict:
            unpacked, msg_keys = flatten_message(value, unpacked, new_key, msg_keys)
            continue
        if type(value) == list and list_contains_dict(value):
            for idx in range(len(value)):
                if value[idx] == None:
                    value[idx] = null_value
                if type(value[idx]) == dict:
                    key_with_idx = f"{new_key}{seperator}idx{idx}"
                    unpacked, msg_keys = flatten_message(
                        value[idx], unpacked, key_with_idx, msg_keys
                    )
                    value[idx] = str(value[idx])
        if value == None:
            value = null_value
        unpacked[new_key] = value
        msg_keys.add(new_key)

    return unpacked, msg_keys


def list_contains_dict(list_to_check):
    for i in list_to_check:
        if type(i) == dict:
            return True
    return False
