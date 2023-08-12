from flask import Blueprint

credentials_route = Blueprint("credentials", __name__)

from . import views
