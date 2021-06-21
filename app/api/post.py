from werkzeug.wrappers import request
from app.api import bp
from app.auth import auth
from app.blog_model import Blog

@bp.route('/post', methods=['GET'])
@auth
def add_post(user=None):
    json = request.json.get
    body = json('body')
    title = json('title')
    id = json('id')
    blog = None
    if id:
        try:
            blog = Blog.query.get(id)
            if not blog:
                return {'error': 'Blog with that id does not exist'}
        except:
            return {'error': 'Invalid blog id'}
    if Post.query.filter-
    
