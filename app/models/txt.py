from datetime import datetime, timezone

from app.misc.sort.tag_sort import tag_sort
from app.misc import hasget
from app import db
from app.models.junctions import xtxts

txt_replies = db.Table("txt_replies",
    db.Column('txt', db.Integer, db.ForeignKey('txt.id')),
    db.Column('reply', db.Integer, db.ForeignKey('txt.id')))

class Txt(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    value = db.Column(db.Unicode)
    about = db.Column(db.Unicode)
    seen = db.Column(db.Boolean, default=False)
    dm = db.Column(db.Boolean, default=False)
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
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        db.session.commit()

    def __init__(self, data):
        value = hasget(data, 'value')
        if value:
            tags = hasget(data, 'tags', [])
            words = value.split(' ')  # TODO trim double spaces
            phrases = []
            length = len(words)
            for idx, word in enumerate(words):
                phrases.append(word)
                for i in range(idx+1, length):
                    word = word + ' ' + words[i]
                    phrases.append(word)
            for phrase in phrases:
                if phrase not in [t['value'] for t in tags]:
                    tags.append({'value': phrase})
            data['tags'] = tags
        db.session.add(self)
        self.edit(data)

    def dict(self, **kwargs):
        uid = None
        seen = None
        joined = None
        if 'user' in kwargs:
            user = kwargs['user']
            uid = user.id
            row = db.engine.execute(xtxts.select().where(xtxts.c.user_id == uid)
                                    .where(xtxts.c.txt_id == self.id)).first()
            if row:
                seen = row['seen']
            joined = user.in_txt(self)
        data = {
            'id': self.id,
            'tags': self.tags,
            'about': self.about,
            'dm': self.dm,
            'value': self.value,
            'joined': joined,
            'replies': self.replies.count(),
            'txts': self.txts.count()
        }
        # if hasget(kwargs, 'include_tags'):
        #     data['tags'] = self.tags
        if self.user:
            data['user'] = self.user.dict()
        if seen is False:
            data['unseen'] = True
        if self.dm:
            data['users'] = [user.id for user in self.users]
        txt_id = hasget(kwargs, 'txt')
        if txt_id:
            txt = Txt.query.get(txt_id)
            if txt and txt.user:
                owner_id = txt.user.id
                owner_replies = self.replies.filter(Txt.user_id == owner_id).count()
                data['ownerReplies'] = owner_replies
            else:
                print(f'txt {txt_id} in **kwargs in txt.dict() call not found')
                # TODO-log
        else:
            txt_id = hasget(kwargs, 'txt')
            if txt_id:
                txt = Txt.query.get(txt_id)
                if txt:
                    owner_id = txt.user_id
                    owner_replies = self.replies.filter(Txt.user_id == owner_id).count()
                    data['ownerReplies'] = owner_replies
                else:
                    print('txt in **kwargs in txt.dict() call not found')
                    # TODO-log
        return data

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
            db.session.commit()
