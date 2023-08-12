from flask import Blueprint

data_view_route = Blueprint("data_view", __name__)

from . import views
