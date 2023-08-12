from flask import Flask, make_response, render_template, request
import json
import webview
import os

from . import paths


# Server setup and config
app = Flask(
    __name__, static_folder=paths.static_dir, template_folder=paths.template_dir
)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1  # Disable caching

if not os.path.isdir(paths.output_dir):
    os.mkdir(paths.output_dir)

if not os.path.isdir(paths.app_data_dir):
    os.mkdir(paths.app_data_dir)

if not os.path.isdir(paths.auth_dir):
    os.mkdir(paths.auth_dir)

if not os.path.isdir(paths.db_dir):
    os.mkdir(paths.db_dir)

window = webview.create_window(
    "F-R-O-G", app, min_size=(800, 800), width=1600, height=1000
)

from .globals import context


@app.before_request
def verify_token():
    if (
        context.instance_is_running()
        and not request.cookies.get("webview-token") == webview.token
    ):
        return make_response({"message": "I´m a teapot."}, 418)


# Avoid caching and prevent a text/html content to be send on errors
@app.after_request
def handle_response(response):
    if not context.instance_is_running():
        context.set_instance_is_running()
        response.set_cookie("webview-token", webview.token)
    response.headers["Cache-Control"] = "no-store"
    if response.status_code == 500:
        if "<!doctype html>" in str(response.get_data()):
            response.headers["Content-Type"] = "application/json"
            response.set_data(json.dumps({"message": "Internal server error."}))
    return response


@app.route("/")
def app_root():
    return render_template("startup.html")


@app.route("/home")
def app_home():
    return render_template("welcome.html")


# Import blueprints and register
from .credentials import credentials_route
from .name_id_map import name_id_map_route
from .scraper import scraper_route
from .data_view import data_view_route
from .authorize_client import authorize_client_route
from .error_log import error_log_route

app.register_blueprint(credentials_route, url_prefix="/credentials")
app.register_blueprint(name_id_map_route, url_prefix="/name-id-map")
app.register_blueprint(scraper_route, url_prefix="/scraper")
app.register_blueprint(data_view_route, url_prefix="/data")
app.register_blueprint(authorize_client_route, url_prefix="/authorize-client")
app.register_blueprint(error_log_route, url_prefix="/error-log")
