from flask import Blueprint

authorize_client_route = Blueprint("authhorize_client", __name__)

from . import views
