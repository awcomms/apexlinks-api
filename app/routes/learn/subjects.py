from app.routes import bp
from app.misc.cdict import cdict
from app.models.learn.subject import Subject

@bp.route('/subjects', methods=['GET'])
def get_subjects():
    return cdict(Subject.query)