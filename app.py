from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask import jsonify
from flask_login import LoginManager

import numpy as np


eeg_data_instance = None

def minmax_downsample(data, num_points):
    """ Downsample the data by taking min and max in chunks corresponding to each pixel width. """
    chunk_size = int(len(data) / num_points)
    downsampled = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        downsampled.append(min(chunk))
        downsampled.append(max(chunk))
    return downsampled[:num_points]  # Ensure we only return the exact number of points needed


class EEGData:
    def __init__(self, filename=None):
        self.filename = filename
        self.data = self.load_data()
        self.sample_rate = 8000  # Hz

    def load_data(self):
        return np.random.randn(8000*60*10, 2)

    def get_window_data(self, start_second, window_length=15):
        start_sample = int(start_second * self.sample_rate)
        end_sample = start_sample + int(window_length * self.sample_rate)
        return self.data[start_sample:end_sample, 0]



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
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



# Create tables if not exist
with app.app_context():
    if not os.path.exists('users.db'):
        db.create_all()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'Username already exists'
        new_user = User(username=username)
        new_user.set_password(password)
        if not new_user.role:  # Just in case, but not strictly necessary with the default set
            new_user.role = 'user'
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

from flask import jsonify, request





@app.route('/list-subjects', methods=['GET'])
@login_required
def list_subjects():
    subjects = Subject.query.all()
    return jsonify([{'id': subject.id} for subject in subjects])  # Adjust according to your data model


@app.route('/get-subject-info/<subject_id>', methods=['GET'])
@login_required
def get_patient_details(subject_id):
    if not subject_id:
        return jsonify({'id': 'N/A', 'last_recorded_time': 'N/A', 'battery_status': 'N/A'})

    subject = Subject.query.filter_by(id=subject_id).first()
    if subject:
        last_recording = Recording.query.filter_by(subject_id=subject_id).order_by(Recording.last_recorded_time.desc()).first()
        last_device_status = DeviceStatus.query.filter_by(subject_id=subject_id).order_by(DeviceStatus.id.desc()).first()

        details = {
            'id': subject.id,
            'last_recorded_time': last_recording.last_recorded_time if last_recording else 'N/A',
            #'last_recorded_time': last_recording.last_recorded_time.strftime("%Y-%m-%d %H:%M:%S") if last_recording else 'N/A',
            'battery_status': last_device_status.battery_status if last_device_status else 'N/A'
        }
        return jsonify(details)
    else:
        return jsonify({'id': 'N/A', 'last_recorded_time': 'N/A', 'battery_status': 'N/A'}), 200

@app.route('/init-eeg', methods=['POST'])
@login_required
def init_eeg():
    global eeg_data_instance
    subject_id = request.form.get('subject_id')
    eeg_data_instance = EEGData()  # Assume filename or subject_id leads to file retrieval
    total_seconds = len(eeg_data_instance.data) / eeg_data_instance.sample_rate
    return jsonify({"message": "EEG data loaded successfully", "total_seconds": total_seconds}), 200



@app.route('/get-eeg-window', methods=['GET'])
@login_required
def get_eeg_window():
    start_second = request.args.get('start_second', type=float)
    window_length = request.args.get('window_length', default=15, type=int)
    canvas_width = request.args.get('canvas_width', type=int)  # Get canvas width from the request

    if not eeg_data_instance:
        return jsonify({'error': 'EEG data not initialized'}), 400

    window_data = eeg_data_instance.get_window_data(start_second, window_length)
    if canvas_width:
        window_data = minmax_downsample(window_data, canvas_width)  # Downsample the data to match the canvas width

    return jsonify(list(window_data))  # Convert numpy array to list for JSON serialization



@app.route('/')
@login_required
def index():
    subjects = Subject.query.all()  # Fetch all subjects from the database
    return render_template('index.html', subjects=subjects)




if __name__ == "__main__":
    app.run(ssl_context='adhoc')


