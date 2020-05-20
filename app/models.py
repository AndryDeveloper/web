from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    status = db.Column(db.String(120))
    lesson = db.Column(db.String(120))
    You_homeworks = db.relationship('You_homework', backref='author', lazy='dynamic')
    delete_status = db.Column(db.String(120))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '{}'.format(self.delete_status)


class You_homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(140))
    body = db.Column(db.String(140))
    files = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '{}'.format(self.number)

class Homeworks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(120))
    lesson = db.Column(db.String(140))
    files = db.Column(db.String(140))
    comments = db.Column(db.String(140))

    def __repr__(self):
        return '{}'.format(self.number)


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    lesson = db.Column(db.String(140))
    access = db.Column(db.String(140))

    def __repr__(self):
        return '{}'.format(self.lesson)