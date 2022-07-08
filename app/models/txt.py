from datetime import datetime, timezone

from app.misc.sort.tag_sort import tag_sort
from app.misc import hasget
from app import db
from app.misc.to_tags import to_tags
from app.models import User
from app.models.junctions import xtxts

txt_replies = db.Table("txt_replies",
    db.Column('txt', db.Integer, db.ForeignKey('txt.id')),
    db.Column('reply', db.Integer, db.ForeignKey('txt.id')))

class Txt(db.Model):
    tags = db.Column(db.JSON, default=[])
    search_tags = db.Column(db.JSON, default=[])
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    value = db.Column(db.Unicode, default='')
    text = db.Column(db.Unicode, default='')
    dm = db.Column(db.Boolean, default=False)
    self = db.Column(db.Boolean, default=False)
    personal = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    replies = db.relationship(
        'Txt',
        secondary=txt_replies,
        primaryjoin=id==txt_replies.c.txt,
        secondaryjoin=id==txt_replies.c.reply,
        lazy='dynamic',
        backref=db.backref('txts', lazy='dynamic'))

    @staticmethod
    def get(tags, limit=0):
        def tag_score(items): return tag_sort(items, tags)
        _sort = tag_score

        def filter(items):
            for idx, item in enumerate(items):
                if item['score'] < limit:
                    items.pop(idx)
            return items

        def run(items):
            _items = _sort(items)
            if limit:
                _items = filter(_items)
            return _items

        return run

    def edit(self, data):
        if data:
            for field in data:
                if hasattr(self, field) and data[field]:
                    setattr(self, field, data[field])
            db.session.commit()

    def __init__(self, data=None):
        value = hasget(data, 'value')
        if value:
            tags = hasget(data, 'search_tags', [])
            search_tags = to_tags(value, tags)
            data['search_tags'] = search_tags

        db.session.add(self)
        self.edit(data)
        if self.user:
            self.user.join(self) #TODO-watch-out
        db.session.commit()
        

    def dict(self, include=None, **kwargs):
        data = {
            'id': self.id,
        }
        if include:
            attrs = ['tags', 'text', 'value', 'self', 'personal', 'search_tags']
            for i in include:
                if i in attrs and hasattr(self, i):
                    data[i] = getattr(self, i)
            if 'user' in include:
                if self.user:
                    data['user'] = self.user.dict(include=['username'])
            if 'time' in include:
                data['time'] = str(self.timestamp)
            if 'seen' in include:
                user = hasget(kwargs, 'user')
                if not user:
                    return Exception(({'error': '`seen` specified in query arg `include` but no logged in user'}, 400))
                uid = user.id
                row = db.engine.execute(xtxts.select().where(xtxts.c.user_id == uid)
                                        .where(xtxts.c.txt_id == self.id)).first()
                if row:
                    seen = row['seen']
                if seen is False:
                    data['unseen'] = True
            if 'users' in include:
                data['users'] = [user.id for user in self.users]
            if 'joined' in include:
                user = hasget(kwargs, 'user')
                # if not user:
                    # return {'error': '`joined` specified in query arg `include` but no logged in user'}, 400
                if user:
                    data['joined'] = user.in_txt(self)
            if 'replyCount' in include:
                data['replyCount'] = self.replies.count()
            if 'ownerReplyCount' in include:
                txt_id = hasget(kwargs, 'txt')
                if not txt_id:
                    return {'error': '`ownerReplyCount` specified in query arg but no txt specified'}, 400
                if txt_id:
                    txt = Txt.query.get(txt_id)
                    if txt:
                        if txt.user:
                            owner_id = txt.user.id
                            owner_replies = self.replies.filter(Txt.user_id == owner_id).count()
                            data['ownerReplies'] = owner_replies
                        else:
                            return {'error': '`ownerReplyCount` specified in query arg `include` but specified txt has no owner'}, 400
                    else:
                        print(f'txt {txt_id} in **kwargs in txt.dict() call not found') # TODO-log
            if 'txtsRepliedToCount' in include:
                data['txtsRepliedToCount'] = self.txts.count()
        return data

    def inherit(self, txt):
        attrs = ['dm', 'personal']
        for field in attrs:
            setattr(self, field, getattr(txt, field))
        if txt.dm:
            for id in txt.dict()['users']:
                user = User.query.get(id)
                user.join(self)
        db.session.commit()

    @staticmethod
    def get_replies(id):
        return Txt.query.get(id).replies

    def replied(self, txt):
        return self.txts.filter(
            txt_replies.c.txt == txt.id
        ).count() > 0

    def reply(self, txt):
        if not self.replied(txt):
            self.txts.append(txt)
            self.inherit(txt)
            self.user.join(txt)
            db.session.commit()

    def unreply(self, txt):
        if self.replied(txt):
            self.txts.remove(txt)
            db.session.commit()
