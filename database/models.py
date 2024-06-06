from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# User model
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    id = db.Column(db.String(10), primary_key=True)  # H1, H2, etc.

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.String(10), db.ForeignKey('subject.id'))
    last_recorded_time = db.Column(db.String(50))

class DeviceStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.String(10), db.ForeignKey('subject.id'))
    battery_status = db.Column(db.String(10))