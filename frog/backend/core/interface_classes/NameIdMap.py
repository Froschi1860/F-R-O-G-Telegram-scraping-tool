from tinydb import Query, where
from frog.backend.core.db import db_name_id_map, data_db_lock


class NameIdMap:
    def __init__(self, channel_ref: str, channel_id: int = None) -> None:
        self._channel_ref = channel_ref
        self._channel_id = channel_id

    def channel_ref(self):
        return self._channel_ref

    def channel_id(self):
        return self._channel_id


def query_name_id_mapping(channel_ref: str) -> NameIdMap:
    with data_db_lock:
        mapping = db_name_id_map.get(where("channel_ref") == channel_ref)
        if mapping == None:
            return None
        return NameIdMap(channel_ref, mapping.get("channel_id"))


def save_name_id_mapping(mapping: NameIdMap) -> None:
    with data_db_lock:
        db_name_id_map.upsert(
            {
                "channel_id": mapping.channel_id(),
                "channel_ref": mapping.channel_ref(),
            },
            where("channel_ref") == mapping.channel_ref(),
        )


def delete_mappings_by_id(channel_id: int) -> list:
    with data_db_lock:
        removed = db_name_id_map.remove(where("channel_id") == channel_id)
        return len(removed) > 0


def query_all_mappings_sorted_by_ref():
    all_docs = []
    with data_db_lock:
        all_docs = list(db_name_id_map.all())
    all_docs.sort(key=lambda e: str.lower(e.get("channel_ref")))
    return all_docs
