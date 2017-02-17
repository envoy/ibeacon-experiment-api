import os
import datetime
import json
import iso8601

import pytz
from flask import Flask
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
pst_tz = pytz.timezone('America/Los_Angeles')


def pst_now():
    utcnow = datetime.datetime.utcnow()
    utcnow = utcnow.replace(tzinfo=pytz.utc)
    return utcnow.astimezone(pst_tz)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    device_model = db.Column(db.String(64))
    os_version = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=True), default=pst_now)

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=pst_now)


class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event = db.Column(db.String(64))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True))
    uploaded_at = db.Column(db.DateTime(timezone=True), default=pst_now)


@app.route("/users", methods=['POST'])
def create_user():
    user = User(
        username=request.form['username'],
        device_model=request.form['device_model'],
        os_version=request.form['os_version'],
    )
    db.session.add(user)
    db.session.commit()
    return str(user.id)


@app.route("/users", methods=['GET'])
def list_users():
    return jsonify(list(map(
        lambda row: dict(id=row[0], name=row[1]),
        db.session.query(User.id, User.username)
            .filter(User.username != 'ipad')
            .order_by(User.username))
    ))


@app.route("/sign-ins", methods=['POST'])
def sign_ins():
    user = db.session.query(User).get(request.form['user_id'])
    signin = SignIn(user=user)
    db.session.add(signin)
    db.session.commit()
    return str(signin.id)


@app.route("/upload-log", methods=['PUT'])
def upload_log():
    data = request.data.decode('utf8')
    lines = data.splitlines()
    user_id = lines[0].strip()
    user = db.session.query(User).get(user_id)

    log = None
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        existing_log = db.session.query(Log).filter_by(id=data['id']).first()
        if existing_log is not None:
            # looks like the log already exists, just skip it
            continue
        log = Log(
            user=user,
            id=data['id'],
            event=data['event'],
            message=data['message'],
            created_at=iso8601.parse_date(data['created_at']).astimezone(pst_tz),
        )
        db.session.add(log)
    db.session.commit()
    return log.id if log is not None else ''


if __name__ == "__main__":
    db.create_all()
    app.run()
