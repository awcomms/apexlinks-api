from app.routes import bp
from app.misc.cdict import cdict
from app.models.learn.term import Term

@bp.route('/terms', methods=['GET'])
def get_terms():
    return cdict(Term.query)