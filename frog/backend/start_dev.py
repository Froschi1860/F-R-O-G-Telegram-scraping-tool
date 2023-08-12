import logging
from contextlib import redirect_stdout
from io import StringIO
import webview
from . import configure_json_encoder, reset_JSONEncoder_default


logger = logging.getLogger(__name__)


def main():
    JSONEncoder_std_default = configure_json_encoder()
    stream = StringIO()
    with redirect_stdout(stream):
        webview.start(debug=True)
    reset_JSONEncoder_default(JSONEncoder_std_default)
