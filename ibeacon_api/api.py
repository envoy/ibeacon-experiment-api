import os
import datetime
import pytz

from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


def pst_now():
    utcnow = datetime.datetime.utcnow()
    utcnow = utcnow.replace(tzinfo=pytz.utc)
    return utcnow.astimezone(pytz.timezone('America/Los_Angeles'))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    device_model = db.Column(db.String(64))
    os_version = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=pst_now)

    sign_ins = db.relationship(
        'SignIn',
        backref=db.backref('user'),
        lazy='dynamic',
    )
    logs = db.relationship(
        'Log',
        backref=db.backref('user'),
        lazy='dynamic',
    )

    def __init__(self, username, device_model, os_version):
        self.username = username
        self.device_model = device_model
        self.os_version = os_version


class SignIn(db.Model):
    __tablename__ = 'signins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=pst_now)


class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event = db.Column(db.String(64))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    uploaded_at = db.Column(db.DateTime, default=pst_now)


@app.route("/users", methods=['POST'])
def users():
    user = User(
        username=request.form['username'],
        device_model=request.form['device_model'],
        os_version=request.form['os_version'],
    )
    db.session.add(user)
    db.session.commit()
    return str(user.id)


@app.route("/sign-ins", methods=['POST'])
def sign_ins():
    user = db.session.query(User).get(request.form['user_id'])
    signin = SignIn(user=user)
    db.session.add(signin)
    db.session.commit()
    return str(signin.id)


@app.route("/upload-log")
def upload_log():
    # TODO: handle uploaded log file from iPhone
    return 'FIXME'




if __name__ == "__main__":
    db.create_all()
    app.run()
