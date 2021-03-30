from app import create_app, db
from app.item_models import Item
from app.user_models import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Item': Item}