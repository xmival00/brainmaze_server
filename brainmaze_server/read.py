import os

import numpy as np # need to install this
import bitstring # this

from insr_parser.parser import InsrParser # also this from the root of the attached file

def load_raw(path_raw):
    conversion_factor = 906 / 1e3  # to uV
    failed = False
    try:
        ts_start, alcp_rev, measurements, waveforms, session_info, program_info = InsrParser().parse(path_raw)

    except:
        failed = True

    if failed == False:
        fs = session_info[0].recording_session.sampling_freq

        ch1_idx = session_info[0].recording_session.scan_channel_configs[0].chan1_terminal1
        ch2_idx = session_info[0].recording_session.scan_channel_configs[0].chan1_terminal2
        ch3_idx = session_info[0].recording_session.scan_channel_configs[0].chan2_terminal1
        ch4_idx = session_info[0].recording_session.scan_channel_configs[0].chan2_terminal2

        ch1_name = 'e' + str(ch1_idx+1) + '-' + 'e' + str(ch2_idx+1)
        ch2_name = 'e' + str(ch3_idx+1) + '-' + 'e' + str(ch4_idx+1)

        x1 = [meas.ch1.astype(np.float64) * conversion_factor for meas in measurements]
        x2 = [meas.ch2.astype(np.float64) * conversion_factor for meas in measurements]

        x1 = np.concatenate(x1)
        x2 = np.concatenate(x2)

        return ts_start, fs, ch1_name, x1, ch2_name, x2

