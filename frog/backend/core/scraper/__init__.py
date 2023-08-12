from flask import Blueprint

scraper_route = Blueprint("scraper", __name__)

from . import views
