from flask import request
from app.routes import bp
from app.misc.world.get import states

@bp.route('/states', methods=['GET'])
def get_states():
    a = request.args.get
    country = a('country')
    print(country)
    return {'items': states(country)}