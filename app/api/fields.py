from app.api import bp
from app.models import Field
from app.item_models import Item
from flask import request, jsonify
from flask_jwt_extended import jwt_required

def add_field(text):
    if not Field.query.filter_by(text=text).first():
        Field(text)
    return {}, 201

@bp.route('/fields/<q>', methods=['GET'])
def get_fields(q):
    return jsonify([{ 'id': f.id, 'text': f.name } for f in Field.query.search('"' + q + '"')])