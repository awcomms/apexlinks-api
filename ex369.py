from app import create_app, db
from app.message_models import Message
from app.room_models import Room
from app.user_model import User, xrooms
from app.sub_models import Sub

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, \
        'xrooms': xrooms, 'Message': Message, 'Sub': Sub, 'Room': Room}