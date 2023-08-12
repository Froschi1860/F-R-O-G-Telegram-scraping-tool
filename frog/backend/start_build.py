import webview
from tendo import singleton
from frog.backend import configure_json_encoder, reset_JSONEncoder_default


def main():
    me = singleton.SingleInstance()
    JSONEncoder_std_default = configure_json_encoder()
    webview.start()
    reset_JSONEncoder_default(JSONEncoder_std_default)


if __name__ == "__main__":
    main()
