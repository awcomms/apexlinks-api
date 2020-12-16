from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import geo, items, blog, forums, users, errors, tokens