
import os
import numpy as np
import scipy.signal as signal

def get_files(path, endings=None, creation_time=False):
    """File list generator.

        For each file in path directory and subdirectories with endings from endings_tuple returns path in a list variable

        path is a string, the path to the directory where you wanna search specific files.

        endings_tuple is a tuple of any length

        The function returns paths to all files in folder and files in all subfolders as well.

        .. code-block:: python

            from best.files import get_files
            import pandas as pd

            path = "root/data"
            files_list = get_files(path, ('.jpg', '.jpeg'))
            files_pd = pd.DataFrame(files_list)

            def get_FID(x):
                temp = x['path'].split('\\')
                return temp[len(temp) - 1][0:-4]
            files_pd = files_pd.rename(columns={0: "path"})
            files_pd['fid'] = files_pd.apply(lambda x: get_FID(x), axis=1)
        """

    if isinstance(endings, str):
        endings = (endings, )

    if isinstance(endings, type(None)):
        data = [os.path.join(root, name)
                for root, dirs, files in os.walk(path)
                for name in files]

        data += [os.path.join(root, dir)
                for root, dirs, files in os.walk(path)
                for dir in dirs]
    else:
        data = [os.path.join(root, name)
                for root, dirs, files in os.walk(path)
                for name in files
                if name.endswith(endings)]

        data += [os.path.join(root, dir)
                for root, dirs, files in os.walk(path)
                for dir in dirs
                if dir.endswith(endings)]


    data = [file for file in data if not '._' in file]
    data.sort()

    if creation_time == False:
        return data

    creation_times = [os.stat(path).st_ctime for path in data]
    data = np.array(data)
    creation_times = np.array(creation_times)
    idx = creation_times.argsort()
    sorted_data = data[idx]
    sorted_creation_times = creation_times[idx]
    return sorted_data, sorted_creation_times


class LowFrequencyFilter:
    """
        Parameters
        ----------
        fs : float
            sampling frequency
        cutoff : float
            frequency cutoff
        n_decimate : int
            how many times the signal will be downsampled before the low frequency filtering
        n_order : int
            n-th order filter used for filtration
        dec_cutoff : float
            relative frequency at which the signal will be filtered when downsampled
        filter_type : str
            'lp' or 'hp'
        ftype : str
            'fir' or 'iir'


        .. code-block:: python

            LFFilter = LowFrequencyFilter(fs=fs, cutoff=cutoff_low, n_decimate=2, n_order=101, dec_cutoff=0.3, filter_type='lp')
            X_inp = np.random.randn(1e4)
            X_outp = LFilter(X_inp)
    """

    __version__ = '0.0.2'

    def __init__(self, fs=None, cutoff=None, n_decimate=1, n_order=None, dec_cutoff=0.3, filter_type='lp', ftype='fir'):
        self.fs = fs
        self.cutoff = cutoff
        self.n_decimate = n_decimate
        self.dec_cutoff = dec_cutoff
        self.filter_type = filter_type

        self.n_order = n_order
        self.ftype = ftype

        self.n_append = None

        self.design_filters()

    def design_filters(self):
        if self.ftype == 'fir':
            if isinstance(self.n_order, type(None)): self.n_order = 101
            self.n_append = (2 * self.n_order) * (2**self.n_decimate)

            self.a_dec = [1]
            self.b_dec = signal.firwin(self.n_order, self.dec_cutoff, pass_zero=True)
            self.b_dec /= self.b_dec.sum()

            self.a_filt = [1]
            self.b_filt = signal.firwin(self.n_order, 2 * self.cutoff / (self.fs/2**self.n_decimate), pass_zero=True)
            self.b_filt /= self.b_filt.sum()

        elif self.ftype == 'iir':
            if isinstance(self.n_order, type(None)): self.n_order = 3
            self.n_append = (2 * self.n_order) * (2**self.n_decimate)

            self.b_dec, self.a_dec = signal.butter(self.n_order, self.dec_cutoff, btype='low')
            self.b_filt, self.a_filt = signal.butter(self.n_order,  2 * self.cutoff / (self.fs/2**self.n_decimate), btype='low')

        else: raise AssertionError(f'[INPUT ERROR]: ftype must be \'iir\' or \'fir\'')

    def decimate(self, X):
        X = signal.filtfilt(self.b_dec, self.a_dec, X)
        return X[::2]

    def upsample(self, X):
        X_up = np.zeros(X.shape[0] * 2)
        X_up[::2] = X
        X_up = signal.filtfilt(self.b_dec, self.a_dec, X_up) * 2
        return X_up

    def filter_signal(self, X):
        # append for filter
        X = np.concatenate((np.zeros(self.n_append), X, np.zeros(self.n_append)), axis=0)

        # append to divisible by 2
        C = int(2**np.ceil(np.log2(X.shape[0] + 2*self.n_append))) - X.shape[0]
        X = np.append(np.zeros(C), X)

        for k in range(self.n_decimate):
            X = self.decimate(X)

        X = signal.filtfilt(self.b_filt, self.a_filt, X)

        for k in range(self.n_decimate):
            X = self.upsample(X)
        #X = self.upsample(X)

        X = X[self.n_append + C : -self.n_append]
        return X


    def __call__(self, X):
        # append for filter
        X_orig = X.copy()
        X = self.filter_signal(X)
        if self.filter_type == 'lp': return X
        if self.filter_type == 'hp': return X_orig - X

    def resample(x, fsamp_old, fsamp_new):
        '''
        :param x: input signal
        :param fsamp_old: original sampling frequency
        :param fsamp_new: new sampling frequency
        :return: interpolated signal at required sampling positions
        '''

        if fsamp_old == fsamp_new:
            return x

        nans = np.isnan(x)
        var = np.nanstd(x)
        mu = np.nanmean(x)
        x = (x - mu) / var
        x[np.isnan(x)] = 0

        xp = np.linspace(0, 1, len(x))
        xi = np.linspace(0, 1, int(np.round(len(x)*fsamp_new/fsamp_old)))

        # xi = np.arange(0, len(x), fsamp_old / fsamp_new) / fsamp_old  # nove navzorkovana casova osa v sekundach
        # xp = np.arange(0, len(x)) / fsamp_old  # puvodne navzorkovana casova osa v sekundach
        x = np.interp(xi, xp, x)
        nans = np.interp(xi, xp, nans)


        x[nans >= 0.5] = np.NaN
        x = (x * var) + mu
        return x

    def detrend(y, x=None, y2=None):
        if isinstance(x, type(None)):
            x = np.linspace(0, 1, y.shape[0])

        a = (y[0] - y[-1]) / (x[0] - x[-1])
        b = y[0] - (x[0]*a)
        if isinstance(y2, type(None)):
            return y - (x*a+b)

        return y - (x * a + b), y2 - (x*a+b)

    def find_peaks(y):
        position = []
        value = []
        for k in range(1, y.__len__() -1):
            if y[k-1] < y[k] and y[k+1] < y[k]:
                position += [k]
                value += [y[k]]
        return np.array(position), np.array(value)