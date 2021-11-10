from app.routes import bp
from flask import request
from app.vars.postalAddress import _city, _state, _country
from app.models.market import Market

@bp.route('/markets', methods=['GET'])
def get_markets():
    a = request.args.get
    country = a('country')
    state = a('state')
    city = a('city')
    postalCode = a('postalCode')
    query = Market.query
    if country:
        query = Market.query.filter(Market.postalAddress[_country]==country)
    if state:
        query = query.filter(Market.postalAddress[_state]==state)
    if city:
        query = query.filter(Market.postalAddress[_city]==city)
    list = [{'text': m.name, 'id': m.id} for m in query]
    return {'res': list}