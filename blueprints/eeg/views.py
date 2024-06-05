from flask import Blueprint, request
from flask_login import login_required
from flask import jsonify
from .utils import EEGData

eeg_data_instance = None

blueprint_eeg = Blueprint('eeg', __name__)

@blueprint_eeg.route('/init-eeg', methods=['POST'])
@login_required
def init_eeg():
    global eeg_data_instance
    file_path = request.form.get('file_path')

    print(file_path)
    eeg_data_instance = EEGData(file_path)  # Assume filename or subject_id leads to file retrieval
    total_seconds = len(eeg_data_instance.x1) / eeg_data_instance.fs
    return jsonify({"message": "EEG data loaded successfully", "total_seconds": total_seconds}), 200


@blueprint_eeg.route('/get-eeg-window', methods=['GET'])
@login_required
def get_eeg_window():
    start_second = request.args.get('start_second', type=float)
    window_length = request.args.get('window_length', default=15, type=int)
    canvas_width = request.args.get('canvas_width', type=int)  # Get canvas width from the request

    if not eeg_data_instance:
        return jsonify({'error': 'EEG data not initialized'}), 400

    print(canvas_width)
    d = eeg_data_instance.get_window_data(start_second, window_length, canvas_width)
    return jsonify(d)
