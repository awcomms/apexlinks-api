import requests
from flask import request
from app.routes import bp
from app.vars.world_api import endpoint

@bp.route('/cities', methods=['GET'])
def get_cities():
    a = request.args.get
    country = a('country')
    state = a('state')
    data = {
        'country': country,
        'state': state
    }
    cities = requests.post(f'/{endpoint}/countries/state/cities', data=data).json()['data']
    return {'res': [{'id': cities.index(c), 'text': c['name']} for c in cities]}