from flask import request
from app.user_model import User
from app.api import bp

@bp.route('paid', methods=['POST'])
def paid():

