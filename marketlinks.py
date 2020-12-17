from flask import jsonify
from app import create_app, db
from app.item_models import Item
from app.geo_models import Nation, State, Town, Place
from app.blog_models import Blog, Blogpost
from app.forum_models import Forum, Forumpost
from app.models import User, Field, Card, Product

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'Town': Town, 'Field': Field, 'Nation': Nation, 'State': State, 'db': db, 'User': User, 'Place': Place, 'jsonify': jsonify, 'Forumpost': Forumpost, 'Product': Product, \
        'Blog': Blog, 'Blogpost': Blogpost, 'Item': Item}