from app import db

blogs = db.Table('blogs',
    db.Column('parent_id', db.Integer, db.ForeignKey('blog.id')),
    db.Column('child_id', db.Integer, db.ForeignKey('blog.id')),
    db.Colum('desc', db.Unicode),
    db.Column('position', db.Integer))

posts = db.Table('posts',
    db.Column('parent_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('child_id', db.Integer, db.ForeignKey('post.id')),
    db.Colum('desc', db.Unicode),
    db.Column('position', db.Integer))