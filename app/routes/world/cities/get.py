from flask import request
from app.routes import bp
from app.misc.world.get import cities

@bp.route('/cities', methods=['GET'])
def get_cities():
    a = request.args.get
    country = a('country')
    state = a('state')
    _cities = cities(country, state)
    return {'items': _cities}