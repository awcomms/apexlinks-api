# from app import db

# blogreplies = db.Table('blogreplies',
#     db.Column('blog_id', db.Integer, db.ForeignKey('blog.id')),
#     db.Column('reply_id', db.Integer, db.ForeignKey('reply.id')),
#     db.Column('position', db.Integer))

# blogs = db.Table('blogs',
#     db.Column('parent_id', db.Integer, db.ForeignKey('blog.id')),
#     db.Column('child_id', db.Integer, db.ForeignKey('blog.id')),
#     db.Column('desc', db.Unicode),
#     db.Column('position', db.Integer))

# replies = db.Table('replies',
#     db.Column('parent_id', db.Integer, db.ForeignKey('reply.id')),
#     db.Column('child_id', db.Integer, db.ForeignKey('reply.id')),
#     db.Column('desc', db.Unicode),
#     db.Column('position', db.Integer))

# # reply_images = db.Table('reply_images',
# #     db.Column('reply_id', db.Integer, db.ForeignKey('reply.id')),
# #     db.Column('image_id', db.Integer, db.ForeignKey('image.id')))