from flask import jsonify
from app import create_app, db
from app.group_models import Group
from app.models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, \
        'Group': Group}