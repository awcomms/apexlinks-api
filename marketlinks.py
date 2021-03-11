from flask import jsonify
from app import create_app, db
from app.event_models import Event
from app.item_models import Item
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, \
        'Event': Event, 'Item': Item}