import os
from tqdm import tqdm
import json
import pandas as pd
from datetime import datetime
import pytz
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
        self.pid = pid

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
        
    def construct_chan_overview(self):
        sub_df = self.files.loc[self.files['subject'] == self.pid].reset_index(drop=True)
        
        # general start
        start_all = sub_df['timestamp'].min() * 1e-6
        start_all = datetime.fromtimestamp(start_all).astimezone(pytz.timezone('US/Central')).strftime("%Y-%m-%d %H:%M:%S")
        
        # general end
        max_time = sub_df[sub_df['timestamp']==sub_df['timestamp'].max()]
        stop_all = max_time['timestamp'] * 1e-6 + max_time['duration_min'] * 60
        stop_all = datetime.fromtimestamp(stop_all.values[0]).astimezone(pytz.timezone('US/Central')).strftime("%Y-%m-%d %H:%M:%S")
        
        # construct interval row
        def _construct_row(row):
            interval_row_1 = {}
            interval_row_2 = {}
            
            class1 = str(row['terminal_1']) + '-' + str(row['terminal_2'])
            class2 = str(row['terminal_3']) + '-' + str(row['terminal_4'])
            
            start = datetime.fromtimestamp(row['timestamp']*1e-6).astimezone(pytz.timezone('US/Central')).strftime("%Y-%m-%d %H:%M:%S")
            stop =  datetime.fromtimestamp(row['timestamp']*1e-6+row['duration']).astimezone(pytz.timezone('US/Central')).strftime("%Y-%m-%d %H:%M:%S") 
                    
            interval_row_1['class'] = class1
            interval_row_2['class'] = class2
            interval_row_1['range0'] = interval_row_2['range0'] = start
            interval_row_1['range1'] = interval_row_2['range1'] = stop
            
            return interval_row_1, interval_row_2
            
        # extract intervals
        intervals = pd.DataFrame()
        fields_to_extract = ['timestamp', 'terminal_1', 'terminal_2', 'terminal_3', 'terminal_4', 'SamplingFrequency']
        for i, metadata in enumerate(sub_df['path_json']):
            duration = sub_df.iloc[i]['duration_min']
            
            with open(metadata, 'r') as f:
                data = json.load(f)
                data = {k: data[k] for k in fields_to_extract}
                data['duration'] = duration * 60
                
                rows = _construct_row(data)
                intervals = pd.concat([intervals, pd.DataFrame(rows)], ignore_index=True)
                                                
        return start_all, stop_all, intervals.to_json(orient='records')
    