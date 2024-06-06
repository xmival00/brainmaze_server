from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime
from database.models import Subject
from flask import jsonify
from .utils import SubjectList, DataScanner
import pytz

blueprint_subjects = Blueprint('subjects', __name__)

@blueprint_subjects.route('/list-subjects', methods=['GET'])
@login_required
def list_subjects():
    # subjects = Subject.query.all()
    print("here we are")
    subjects = SubjectList().subjects
    return jsonify(subjects)  # Adjust according to your data model


@blueprint_subjects.route('/get-subject-info/<subject_id>', methods=['GET'])
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
    
    
@blueprint_subjects.route('/')
@login_required
def index():
    subjects = Subject.query.all()  # Fetch all subjects from the database
    return render_template('index.html', subjects=subjects)