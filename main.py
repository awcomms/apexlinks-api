from app import create_app, db
from app.models import User, Item, Txt, item_items
from app.models.junctions import xtxts
from app.models.learn.note import Note
from app.models.learn.level import Level
from app.models.learn.subject import Subject
from app.models.learn.term import Term
from app.models import Sub

app = create_app()
app.static_folder = 'static'

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Item': Item,
        'Txt': Txt,
        'xtxts': xtxts,
        'Sub': Sub,
        'item_items': item_items,
        'Note': Note,
        'Level': Level,
        'Subject': Subject,
        'Term': Term
    }
