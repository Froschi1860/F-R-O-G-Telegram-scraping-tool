import os
import threading
from tinydb import TinyDB
from tinydb_encrypted_jsonstorage import EncryptedJSONStorage
from frog.backend.core.paths import db_dir


data_db = TinyDB(path=(os.path.join(db_dir, "f-r-o-g_data.db")))
data_db_lock = threading.Lock()

error_db = TinyDB(path=(os.path.join(db_dir, "f-r-o-g_error.json")))
error_db_lock = threading.Lock()

cred_db = TinyDB(
    path=(os.path.join(db_dir, "f-r-o-g_cred.db")),
    storage=EncryptedJSONStorage,
    encryption_key="PASSWORD",
)
cred_db_lock = threading.Lock()


db_cred = cred_db.table("credentials")
db_name_id_map = data_db.table("name_id_map")
db_channels = data_db.table("channels")
db_error_log = error_db.table("error_log")
