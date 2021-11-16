from app.routes import bp
from app.models.learn.level import Level
from app.models.learn.subject import Subject
from app.models.learn.term import Term

@bp.route('/init', methods=['GET'])
def init():
    Subject('Mathematics')
    Subject('English')

    Term('1st Term')
    Term('1st Term')
    Term('3rd Term')

    Level('Grade 1')
    Level('Grade 2')
    Level('Grade 3')
    Level('Grade 4')
    Level('Grade 5')
    Level('Grade 6')
    
    return ''