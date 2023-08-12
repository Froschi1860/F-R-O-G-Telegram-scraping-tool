import time
from tinydb.table import Document
from tinydb.operations import set
from frog.backend.core.db import data_db_lock, db_channels


class ChannelMeta:
    def __init__(
        self,
        refs: list = [],
        last_msg_id: int = 0,
        accessible: bool = True,
        last_access: str = "",
        channel_users: list = [],
        queried_meta: dict = None,
    ) -> None:
        if queried_meta != None:
            self._refs = queried_meta["refs"].copy()
            self._last_msg_id = queried_meta["last_msg_id"]
            self._accessible = queried_meta["accessible"]
            self._last_access = queried_meta["last_access"]
            self._channel_users = queried_meta["channel_users"]
            return
        self._refs = refs.copy()
        self._last_msg_id = last_msg_id
        self._accessible = accessible
        self._last_access = last_access
        self._channel_users = channel_users

    def refs(self) -> list:
        return self._refs.copy()

    def add_ref(self, new_ref: str) -> None:
        self._refs.append(new_ref)

    def last_msg_id(self) -> int:
        return self._last_msg_id

    def set_last_msg_id(self, last_msg_id: int) -> None:
        self._last_msg_id = last_msg_id

    def accessible(self) -> bool:
        return self._accessible

    def set_accessible(self) -> None:
        self._accessible = True

    def reset_accessible(self) -> None:
        self._accessible = False

    def last_access(self) -> str:
        return self._last_access

    def set_last_access(self, date: time.struct_time) -> None:
        self._last_access = time.strftime("%Y-%m-%d %H:%M:%S %Z%z", date)

    def update_channel_users(self, new_users: list):
        existing_users = {1}  # Workaraound since set keyword is overwritten
        existing_users.remove(1)
        existing_users.update(self._channel_users)
        existing_users.update(new_users)
        self._channel_users = list(existing_users)

    def as_dict(self) -> dict:
        return {
            "refs": self._refs.copy(),
            "last_msg_id": self._last_msg_id,
            "accessible": self._accessible,
            "last_access": self._last_access,
            "channel_users": self._channel_users,
        }


def channel_is_known(channel_id: int) -> bool:
    with data_db_lock:
        return db_channels.contains(doc_id=channel_id)


def query_meta_data(channel_id: int) -> ChannelMeta:
    with data_db_lock:
        channel = db_channels.get(doc_id=channel_id)
        if channel == None:
            return None
        return ChannelMeta(queried_meta=channel.get("meta"))


def save_meta_data(channel_id: int, new_meta: ChannelMeta) -> None:
    with data_db_lock:
        db_channels.upsert(Document({"meta": new_meta.as_dict()}, channel_id))


def query_msgs(channel_id: int) -> dict:
    with data_db_lock:
        channel = db_channels.get(doc_id=channel_id)
        if channel == None:
            return None
        return channel.get("msgs")


def query_msgs_as_list(channel_id: int) -> list:
    with data_db_lock:
        channel = db_channels.get(doc_id=channel_id)
        if channel == None:
            return None
        msgs = channel.get("msgs")
        if msgs == None:
            return None
        msgs_as_list = []
        msg_ids = list(msgs.keys())
        msg_ids.sort(key=(lambda e: int(e)))
        for msg_id in msg_ids:
            msgs_as_list.append(msgs[msg_id])
        return msgs_as_list


def save_msgs(channel_id: int, new_msgs: dict):
    with data_db_lock:
        if not db_channels.contains(doc_id=channel_id):
            db_channels.insert(
                Document({"meta": ChannelMeta().as_dict(), "msgs": {}}, channel_id)
            )
        msgs = db_channels.get(doc_id=channel_id).get("msgs")
        if msgs == None:
            msgs = {}
        for msg_id, msg in new_msgs.items():
            if str(msg_id) not in msgs.keys():
                msgs[str(msg_id)] = msg
        db_channels.update(set("msgs", msgs), doc_ids=[channel_id])


def delete_msgs(channel_id: int) -> bool:
    with data_db_lock:
        channel = db_channels.get(doc_id=channel_id)
        if channel == None:
            return False
        meta = channel.get("meta")
        meta["last_msg_id"] = 0
        db_channels.update(set("meta", meta), doc_ids=[channel_id])
        db_channels.update(set("msgs", {}), doc_ids=[channel_id])
        return True


def delete_channel(channel_id: int) -> bool:
    with data_db_lock:
        return db_channels.remove(doc_ids=[channel_id])[0] == channel_id
