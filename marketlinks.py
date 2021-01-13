from flask import jsonify
from app import create_app, db
from app.item_models import Item
from app.geo_models import Nation, State, Town
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'Town': Town, 'Nation': Nation, 'State': State, 'db': db, 'User': User, \
        'Item': Item}