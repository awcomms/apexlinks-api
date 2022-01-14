from app import create_app, db
from flask_socketio import SocketIO
from app.models import User, Item
from app.models.learn.note import Note
from app.models.learn.level import Level
from app.models.learn.subject import Subject
from app.models.learn.term import Term

app = create_app()
app.static_folder = 'static'
socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Item': Item,
        'Note': Note,
        'Level': Level,
        'Subject': Subject,
        'Term': Term
    }
