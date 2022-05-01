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
    id = _data('id')
    id = try_int(id)
    if not id:
        print('bad id: ', id)
        return {'error': "request body parameter 'id' should be a number"}, 400
    
    note = Note.query.get(id)
    if not note:
        return {'error': f'note {id} not found'}, 400
    
    edit_data = {
        'name': _data('name'),
        'body': _data('body'),
    }

    # edit_data = {}
    # name = _data('name')
    # if name:
    #     edit_data['name'] = name

    # body = _data('body')
    # if body:
    #     edit_data['body'] = body
    
    level = _data('level')
    if level:
        level = Level.query.get(level)
        if not level:
            return {'error': f'level {id} not found'}
        edit_data['level'] = level

    subject = _data('subject')
    if subject:
        subject = Subject.query.get(subject)
        if not subject:
            return {'error': f'subject {id} not found'}
        edit_data['subject'] = subject

    term = _data('term')
    if term:
        term = Term.query.get(term)
        if not term:
            return {'error': f'term {id} not found'}
        edit_data['term'] = term
    
    note.edit(edit_data)
    return note.dict()

@bp.route('/note/<int:id>', methods=['GET'])
def get_note(id):
    # args = request.args.get
    # id = args(id)
    # id = try_int(id)
    # if not id:
    #     return {'error': "request body parameter 'id' should be a number"}
    note = Note.query.get(id)
    if not note:
        return {'error': f'note {id} not found'}
    return note.dict()

@bp.route('/note', methods=['GET'])
def get_notes():
    args = request.args.get

    level = args('level')
    if level and level != 'null':
        level = try_int(level)
        if not level:
            return {'error': f"request body parameter 'level' should be a number"}, 400
    subject = args('subject')
    if subject and level != 'null':
        subject = try_int(subject)
        if not subject:
            return {'error': f"request body parameter 'subject' should be a number"}, 400
    term = args('term')
    if term and level != 'null':
        term = try_int(term)
        if not term:
            return {'error': f"request body parameter 'term' should be a number"}, 400
    print(level, subject, term)
    notes = Note.query.filter(Note.level_id==level)
    notes = notes.filter(Note.subject_id==subject)
    notes = notes.filter(Note.term_id==term)
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