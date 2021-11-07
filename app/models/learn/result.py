from app import db

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.Unicode)
    grade = db.Column(db.Unicode)
    score = db.Column(db.Unicode)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    def __init__(self, user, subject, score):
        self.user = user
        self.subject = subject
        self.score = score
        db.session.add(self)
        db.session.commit()

    def dict(self):
        return {
            'id': self.id,
            'subject': self.subject.label,
            'score': self.score
        }