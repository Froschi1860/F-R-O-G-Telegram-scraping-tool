from flask import Blueprint

error_log_route = Blueprint("error_log", __name__)

from . import views
