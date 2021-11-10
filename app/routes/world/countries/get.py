import requests
from app.routes import bp
from app.vars.world_api import endpoint

@bp.route('/countries', methods=['GET'])
def get_countries():
    countries = requests.get(f'/{endpoint}/countries/iso').json()['data']
    return {'res': [{'id': countries.index(c), 'text': c['name']} for c in countries]}