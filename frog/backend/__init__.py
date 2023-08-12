from datetime import datetime
import json
from . import core


def configure_json_encoder():
    JSONEncoder_olddefault = json.JSONEncoder.default

    def JSONEncoder_newdefault(self, obj):
        if isinstance(obj, bytes):
            return list(obj)
        if isinstance(obj, datetime):
            return datetime.isoformat(obj)
        return JSONEncoder_olddefault(self, obj)

    json.JSONEncoder.default = JSONEncoder_newdefault

    return JSONEncoder_olddefault


def reset_JSONEncoder_default(old_default):
    json.JSONEncoder.default = old_default
