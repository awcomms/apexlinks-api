from app.routes import bp
from flask import request
from app.vars.postalAddress import _city, _state, _country
from app.models.market import Market

@bp.route('/markets', methods=['POST'])
def add_market():
    rj = request.json.get
    country = rj('country')
    state = rj('state')
    city = rj('city')
    postalAddress = {
        _country: country,
        _state: state,
        _city: city
    }
    m = Market(postalAddress)
    return m.dict()