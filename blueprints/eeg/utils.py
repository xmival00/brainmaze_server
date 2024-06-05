import numpy as np
from brainmaze_server.read import load_raw
from brainmaze_server.utils import LowFrequencyFilter

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
