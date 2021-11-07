from app.models.learn.subject import Subject
from app.models.learn.term import Term
from app.models.learn.level import Level
from app.misc.try_int import try_int
from app import db
from app.routes import bp
from flask import request
from app.models.learn.note import Note
from app.misc.cdict import cdict

@bp.route('/note', methods=['PUT'])
def edit_note():
    _data = request.json.get
    print(request.get_json())
    id = _data('id')
    print('g id: ', id)
    id = try_int(id)
    if not id:
        print('bad id: ', id)
        return {'error': "body param 'id' should be a number"}, 400
    note = Note.query.get(id)
    if not note:
        return {'error': f'note {id} not found'}, 400
    edit_data = {
        'name': _data('name'),
        'body': _data('body'),
    }
    level = _data('level')
    level = Level.query.get(level)
    if not level:
        return {'error': f'level {id} not found'}

    subject = _data('subject')
    subject = Subject.query.get(subject)
    if not subject:
        return {'error': f'subject {id} not found'}

    term = _data('term')
    term = Term.query.get(term)
    if not term:
        return {'error': f'term {id} not found'}
    note.edit(edit_data)
    return note.dict()

@bp.route('/note/<int:id>', methods=['GET'])
def get_note(id):
    # args = request.args.get
    # id = args(id)
    # id = try_int(id)
    # if not id:
    #     return {'error': "body param 'id' should be a number"}
    note = Note.query.get(id)
    if not note:
        return {'error': f'note {id} not found'}
    return note.dict()

@bp.route('/note', methods=['GET'])
def get_notes():
    args = request.args.get
    level = args('level')
    if level:
        level = try_int(level)
        if not level:
            return {'error': f"body param 'level' should be a number"}
    subject = args('subject')
    if subject:
        subject = try_int(subject)
        if not subject:
            return {'error': f"body param 'subject' should be a number"}
    term = args('term')
    if term:
        term = try_int(term)
        if not term:
            return {'error': f"body param 'term' should be a number"}
    notes = Note.query.filter(Note.level_id==level)
    notes = Note.query.filter(Note.subject_id==subject)
    notes = Note.query.filter(Note.term_id==term)
    notes = notes.order_by(Note.time.desc())
    return cdict(notes)

@bp.route('/note', methods=['POST'])
def add_note():
    _data = request.json.get
    name = _data('name')
    body = _data('body')
    level = _data('level')
    level = Level.query.get(level)
    if not level:
        return {'error': f'level {id} not found'}

    subject = _data('subject')
    subject = Subject.query.get(subject)
    if not subject:
        return {'error': f'subject {id} not found'}

    term = _data('term')
    term = Term.query.get(term)
    if not term:
        return {'error': f'term {id} not found'}
    add_data = {
        'level': level,
        'subject': subject,
        'term': term,
        'name': name,
        'body': body
    }
    note = Note(add_data)
    return note.dict()
