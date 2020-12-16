from app.api import bp
from app.geo_models import Place, Town, State, Nation
from flask import request, jsonify

#places
@bp.route('/search_items_for_places', methods=['GET'])
def search_items_for_places():
    a = request.args.get
    q = a('q')
    page = a('page')
    resources = Item.query.search('"' + q + '"', sort=True).paginate(page, 11, False)
    data = {
        'items': [item.user.place.dict() for item in resources.items],
        'total': resources.total,
        'pages': resources.pages
    }
    return jsonify(cdict(data))

@bp.route('/search_places_in_town', methods=['GET'])
def search_places_in_town():
    a = request.args.get
    q = a('q')
    town_id = a('town_id')
    return jsonify([{'id': place.id, 'text': place.name} for place in Place.query.search('"' + q + '"').filter_by(town_id=town_id)])

@bp.route('/search_places_by_page', methods=['GET'])
def search_places_by_page():
    a = request.args.get
    q = a('q')
    page = a('page')
    return jsonify(cdict(Place.query.search('"' + q + '"'), page))

@bp.route('/search_places', methods=['GET'])
def search_places():
    a = request.args.get
    q = a('q')
    return jsonify([{'id': place.id, 'text': place.name} for place in Place.query.search('"' + q + '"')])
#places

@bp.route('/search_towns_in_state', methods=['GET'])
def search_towns_in_state():
    a = request.args.get
    q = a('q')
    state_id = a('state_id')
    return jsonify([{'id': town.id, 'text': town.name} for town in Place.query.search('"' + q + '"').filter_by(state_id=state_id)])

@bp.route('/search_towns', methods=['GET'])
def search_towns():
    a = request.args.get
    q = a('q')
    return jsonify([{'id': town.id, 'text': town.name} for town in Town.query.search('"' + q + '"')])

@bp.route('/search_states_in_nation', methods=['GET'])
def search_states_in_nation():
    a = request.args.get
    q = a('q')
    if q == '':
        return jsonify([{'id': state.id, 'text': state.name} for state in State.query.filter_by(nation_id=nation_id)])
    nation_id = a('nation_id')
    return jsonify([{'id': state.id, 'text': state.name} for state in State.query.search('"' + q + '"').filter_by(nation_id=nation_id)])

@bp.route('/search_states', methods=['GET'])
def search_states():
    a = request.args.get
    q = a('q')
    return jsonify([{'id': state.id, 'text': state.name} for state in State.query.search('"' + q + '"')])

@bp.route('/search_nations', methods=['GET'])
def search_nations():
    a = request.args.get
    q = a('q')
    if q == '':
        return jsonify([{'id': nation.id, 'text': nation.name} for nation in Nation.query])
    return jsonify([{'id': nation.id, 'text': nation.name} for nation in Nation.query.search('"' + q + '"')])