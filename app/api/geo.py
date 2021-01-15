from app.api import bp
from app.models import cdict
from ip2geotools.databases.noncommercial import DbIpCity
from app.geo_models import Place, Town, State, Nation
from flask import request, jsonify

@bp.route('/ip')
def ip():
    ip = request.args.get('ip')
    response = DbIpCity.get(ip, api_key='free')
    location = {lat: response.latitude, lng: response.longitude}
    return jsonify(location)

@bp.route('/place_saved', methods=['GET'])
def place_saved():
    a = request.args.get
    user_id = a('user_id')
    place_id = a('place_id')
    user = User.query.get(user_id)
    if not user:
        return {}, 301
    place = Place.query.get(place_id)
    if not place:
        return {}, 301
    val = user.place_saved(place_id)
    return jsonify({'res': val})

@bp.route('/save_place', methods=['PUT'])
def save_place():
    token = request.headers['Authorization']
    j = request.json.get
    place_id = j('place_id')
    user = User.query.filter_by(token=token).first()
    place = Place.query.get(place_id)
    if place.user != user:
        return {}, 401
    user.save_place(place)
    return jsonify({'yes': True})

@bp.route('/unsave_place', methods=['PUT'])
def unsave_place():
    token = request.headers['Authorization']
    j = request.json.get
    place_id = j('place_id')
    user = User.query.filter_by(token=token).first()
    place = Place.query.get(place_id)
    if place.user != user:
        return {}, 401
    user.unsave_place(place)
    return jsonify({'yes': True})

@bp.route('/places/<int:id>', methods=['GET'])
def get_place(id):
    return jsonify(Place.query.get(id).dict())

@bp.route('/places/add_tags', methods=['PUT'])
def add_tags():
    j = request.json.get
    for tag in j('tags'):
        Place.query.get(j('id')).add_tag(tag)

@bp.route('/search_places_in_state', methods=['GET'])
def search_places_in_state():
    a = request.args.get
    q = a('q')
    q = q.replace('%20', ' ')
    page = a('page')
    user_id = a('user_id')
    state_id = a('state_id')
    if q == '':
        query = Place.query.filter_by(state_id=state_id)
        dict = cdict(query, page)
        for place in dict['items']:
            place['saved'] = Place.is_saved(place['id'], user_id)
        return jsonify(cdict(Place.query.filter_by(state_id=state_id), page))
    return jsonify(dict)

@bp.route('/search_items_for_places', methods=['GET'])
def search_items_for_places():
    a = request.args.get
    q = a('q')
    q = q.replace('%20', ' ')
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
    q = q.replace('%20', ' ')
    page = a('page')
    return jsonify(cdict(Place.query.search('"' + q + '"'), page))

@bp.route('/search_places', methods=['GET'])
def search_places():
    a = request.args.get
    q = a('q')
    q = q.replace('%20', ' ')
    return jsonify([{'id': place.id, 'text': place.name} for place in Place.query.search('"' + q + '"', sorted=True)])

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

@bp.route('/states')
def states():
    id = request.args.get('id')
    return jsonify([{'id': state.id, 'text': state.name} for state in State.query.filter_by(nation_id=id)])

@bp.route('/nations')
def get_nations():
    return jsonify([{'id': nation.id, 'text': nation.name} for nation in Nation.query])

    a = request.args.get
    q = a('q')
    q = q.replace('%20', ' ')
    if q == '':
        return jsonify([{'id': nation.id, 'text': nation.name} for nation in Nation.query])
    return jsonify([{'id': nation.id, 'text': nation.name} for nation in Nation.query.search('"' + q + '"')])