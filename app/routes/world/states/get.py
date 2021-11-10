import requests
from flask import request
from app.routes import bp
from app.vars.world_api import endpoint

@bp.route('/states', methods=['GET'])
def get_states():
    a = request.args.get
    country = a('country')
    data = {'country': country}
    states = requests.post(f'/{endpoint}/countries/state', data=data).json()['data']['states']
    return {'res': [{'id': states.index(s), 'text': s['name']} for s in states]}