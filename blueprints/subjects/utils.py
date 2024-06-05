import os
from tqdm import tqdm
import json
import pandas as pd
from brainmaze_server.utils import get_files

path_data = '../data'

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