from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask import jsonify
from flask_login import LoginManager
from flask import jsonify, request

from datetime import datetime

import numpy as np
import pandas as pd
import json
import pytz
from tqdm import tqdm

from brainmaze_server.utils import get_files, LowFrequencyFilter
from brainmaze_server.read import load_raw


import scipy.signal as signal

eeg_data_instance = None
path_data = '/Volumes/Boron/CorCadCloudData/cadence/sourcedata'




class SubjectList:
    def __init__(self):
        global path_data
        self.path = path_data
        self.subjects = [d.split('-')[1] for d in os.listdir(self.path) if not '.-' in d and not '._' in d and not '.DS_Store' in d]


class DataScanner:
    def __init__(self, pid='') -> None:
        global path_data
        self.path = path_data

        self.files: pd.DataFrame = None
        self.reload_data(pid)

    def reload_data(self, pid:str = ''):
        files = [f for f in get_files(self.path, 'raw') if not '.-' in f and not '._' in f and pid in f.split(os.sep)[-1] and not '.DS_Store' in f]

        fids = []
        for f_raw in  tqdm(files):
            f_json = f_raw.replace('raw', 'json')
            meta = json.loads(open(f_json, 'r').read())

            fids += [
                {
                    'subject': f_raw.split(os.sep)[-3].split('-')[1],
                    'session': f_raw.split(os.sep)[-2],
                    'inss_id': meta['INSS_id'],

                    'timestamp': meta['timestamp'],
                    'fs': meta['SamplingFrequency'],
                    'duration_min': meta['duration'],
                    'stim': meta['stim_on'],

                    'alcp': meta['alcp_version'],
                    'original_filename': meta['original_name'],
                    'filesize_mb': meta['size_MB'],
                    'computer_id': meta['computer_id'],

                    'path_raw': f_raw,
                    'path_json': f_json,
                }
            ]

        self.files = pd.DataFrame(fids)


def minmax_downsample(data, num_points):
    """ Downsample the data by taking min and max in chunks corresponding to each pixel width. """
    chunk_size = int(len(data) / num_points)
    downsampled = []
    tidx = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]

        amin = np.argmin(chunk)
        amax = np.argmax(chunk)

        if amin < amax:
            i1 = amin
            i2 = amax
        else:
            i1 = amax
            i2 = amin

        downsampled.append(chunk[i1])
        downsampled.append(chunk[i2])
        tidx += [i]
    return downsampled, tidx


class EEGData:
    def __init__(self, filename=None):
        self.filename = filename

        self.ts = None
        self.fs = None
        self.ch1 = None
        self.x1 = None
        self.ch2 = None
        self.x2 = None

        self.recording_trace = None
        self.recording_time = None

        self.canvas_width = None
        self.recording_trace = None
        self.recording_time = None# list(self.time_vector[::int(self.time_vector.shape[0] / 3000)])
        self.recording_range = None

        self.load_data()


    def load_data(self):
        self.ts, self.fs, self.ch1, self.x1, self.ch2, self.x2 = load_raw(self.filename)

        self.ts = self.ts + 120
        self.x1 = self.x1[int(120*self.fs):]
        self.x2 = self.x2[int(120 * self.fs):]

        # b, a = signal.firwin(51, cutoff=0.1, fs=self.fs, window='hann'), [1]
        # self.x1 = self.x1-signal.filtfilt(b,a,self.x1)
        # self.x2 = self.x2-signal.filtfilt(b, a, self.x2)

        if self.fs == 8000:
            n_decimate = 8
        elif self.fs == 2000:
            n_decimate = 6
        else: n_decimate = 4

        LFFilt = LowFrequencyFilter(cutoff=0.5, fs=self.fs, n_decimate=n_decimate, n_order=7, ftype='iir', filter_type='hp')
        self.x1 = LFFilt(self.x1)
        self.x2 = LFFilt(self.x2)

        self.time_vector = (np.arange(self.x1.shape[0]) / self.fs / 60)# + self.ts
        # self.time_vector = [datetime.fromtimestamp(ts).astimezone(pytz.timezone('US/Central')) for ts in self.time_vector]
        # self.time_vector = [
        #     datetime.fromtimestamp(ts).astimezone(pytz.timezone('US/Central')).strftime('%m-%d %H:%M:%S')
        #     for ts in self.time_vector
        # ]


        for k in self.__dict__.keys():
            if isinstance(self.__dict__[k], np.ndarray):
                self.__dict__[k] = list(self.__dict__[k])


    def get_window_data(self, start_second, window_length=15, canvas_width=None):
        start_sample = int(start_second * self.fs)
        end_sample = start_sample + int(window_length * self.fs)

        if canvas_width != self.canvas_width:
            x1ds, _ = minmax_downsample(self.x1, canvas_width)
            x2ds, xtidx = minmax_downsample(self.x2, canvas_width)
            self.recording_trace = [
                list(x1ds),
                list(x2ds),
            ]
            self.recording_time = [self.time_vector[i] for i in xtidx]
            self.canvas_width = canvas_width

            self.recording_range = [
                [np.nanquantile(self.recording_trace[0], 0.01), np.nanquantile(self.recording_trace[0], 0.99)],
                [np.nanquantile(self.recording_trace[1], 0.01), np.nanquantile(self.recording_trace[1], 0.99)],
            ]

        x1_downsampled, _ = minmax_downsample(self.x1[start_sample:end_sample], canvas_width)
        x2_downsampled, tidx = minmax_downsample(self.x2[start_sample:end_sample], canvas_width)
        t_vect = [self.time_vector[i] for i in tidx]

        d = {
            'ch_names': [self.ch1, self.ch2],
            'data': [
                    x1_downsampled,
                    x2_downsampled
                ],
            'time_data': list((np.arange(end_sample-start_sample) / self.fs)[::int(len(t_vect) / canvas_width)]),
            'range_data': [
                [np.nanquantile(x1_downsampled, 0.001), np.nanquantile(x1_downsampled, 0.999)],
                [np.nanquantile(x2_downsampled, 0.001), np.nanquantile(x2_downsampled, 0.999)],
            ],

            'recording_trace': self.recording_trace,
            'recording_time': self.recording_time,
            'start_window': self.time_vector[start_sample],
            'end_window': self.time_vector[end_sample],
            'range_trace': self.recording_range


        }
        return d


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






@app.route('/list-subjects', methods=['GET'])
@login_required
def list_subjects():
    # subjects = Subject.query.all()
    subjects = SubjectList().subjects
    return jsonify(subjects)  # Adjust according to your data model


@app.route('/get-subject-info/<subject_id>', methods=['GET'])
@login_required
def get_patient_details(subject_id):
    default_reply = jsonify({'id': 'N/A', 'last_recorded_time': 'N/A', 'battery_status': 'N/A'})
    if not subject_id:
        return default_reply

    scanner = DataScanner(subject_id)
    df = scanner.files.loc[scanner.files['subject'] == subject_id].reset_index(drop=True)
    df['timestamp'] = [datetime.fromtimestamp(ts/1e6).astimezone(pytz.timezone('US/Central')) for ts in df['timestamp'].to_numpy()]

    df = df[[k for k in df.columns if not 'path_json' in k]]
    if df.__len__():
        return jsonify(df.to_dict(orient='records'))
    else:
        return default_reply, 200

@app.route('/init-eeg', methods=['POST'])
@login_required
def init_eeg():
    global eeg_data_instance
    file_path = request.form.get('file_path')

    print(file_path)
    eeg_data_instance = EEGData(file_path)  # Assume filename or subject_id leads to file retrieval
    total_seconds = len(eeg_data_instance.x1) / eeg_data_instance.fs
    return jsonify({"message": "EEG data loaded successfully", "total_seconds": total_seconds}), 200



@app.route('/get-eeg-window', methods=['GET'])
@login_required
def get_eeg_window():
    start_second = request.args.get('start_second', type=float)
    window_length = request.args.get('window_length', default=15, type=int)
    canvas_width = request.args.get('canvas_width', type=int)  # Get canvas width from the request

    if not eeg_data_instance:
        return jsonify({'error': 'EEG data not initialized'}), 400

    d = eeg_data_instance.get_window_data(start_second, window_length, canvas_width)
    return jsonify(d)


@app.route('/')
@login_required
def index():
    subjects = Subject.query.all()  # Fetch all subjects from the database
    return render_template('index.html', subjects=subjects)




if __name__ == "__main__":

    app.run(ssl_context='adhoc')

