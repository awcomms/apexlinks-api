import requests
from app.routes import bp
from app.misc.world.get import countries

@bp.route('/countries', methods=['GET'])
def get_countries():
    return {'items': countries()}