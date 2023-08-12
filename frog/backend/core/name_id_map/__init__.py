from flask import Blueprint

name_id_map_route = Blueprint("name_id_map", __name__)

from . import views
