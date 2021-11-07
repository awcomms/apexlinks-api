from app import create_app, db
from app.user_model import User
from app.models.learn.note import Note
from app.models.learn.level import Level

app = create_app()
app.static_folder = 'static'

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Note': Note,
        'Level': Level
    }
