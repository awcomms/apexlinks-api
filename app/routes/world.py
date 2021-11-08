from app.routes import bp
from flask import request
import app.misc.countries.get as get

@bp.route('/countries', methods=['GET'])
def get_countries():
    return {'items': get.countries()}

@bp.route('/states', methods=['GET'])
def get_states():
    country = request.args.get('country')
    return {'items': get.states(country)}

@bp.route('/cities', methods=['GET'])
def cities():
    args = request.args.get
    country = args('country')
    state = args('state')
    return {'items': get.cities(country, state)}
