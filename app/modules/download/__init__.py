from flask import Blueprint

download_blue = Blueprint('downlaod', __name__)

from . import views