import pytest

import textwrap
import pandas as pd
from matplotlib import pyplot as plt
from time import time

from insr_parser.parser import InsrParser
from insr_parser.parser_utils import un_chunk
from insr_parser.stim_waveform import amplitude_index_to_volts
from collections import Counter

timestamp = None
class TestParser:
    def test_read_file(self):
        parser = InsrParser(status_msg_callback=self.status_update)
        self.timestamp = time()
        #parser.parse("stim.raw")
        filenames = [
            '2kHz_sample_10Hz_stim_125_us_pulse_1mA.raw',
            '500Hz_sample_10Hz_stim_125us_pulse_1mA.raw'
        ]
#      measurements, waveform_info_list, sessions, programs, items = parser.parse('stim.raw')
#       measurements, waveform_info_list, sessions, programs, items = parser.parse('baseline.raw')
#        measurements, waveform_info_list, sessions, programs, items = parser.parse('stim.raw')
        filename = filenames[0]
        measurements, waveform_info_list, sessions, programs = parser.parse(filename)
        print(f'Parsing {filename}:')
        print(f'Number of Measurement blocks: {len(measurements)}')
        num_points = list()
        for m in measurements:
            num_points.append(len(m.ch1))
        print(Counter(num_points))
        print(f'Number of waveform info blocks: {len(waveform_info_list)}')
        print('First waveform info block:')
        print(textwrap.indent(f'{waveform_info_list[0]}', '   '))
        print(f'Number of  Sessions: {len(sessions)}')
        for session in sessions:
            print(textwrap.indent(f'{session}',"   "))
        print(f'Number of programs: {len(programs)}')
        for p in programs:
            print(p)
#        df = pd.DataFrame(measurements[0].ch1)
#        df.plot()
 #       plt.show()


    def status_update(self, message):
        delta = time() - self.timestamp
        print(f'{delta * 1000:3.2f}ms {message}')
        self.timestamp = time()

    def test_stim_amplitude(self):
        print('\n')
        for i in range(56):
            print(f'{i:3}  {amplitude_index_to_volts(i) * 1000}')

def status_update(message):
    print(f'{message}')


if __name__ == '__main__':
    parser = InsrParser()
    timestamp = time()
    # parser.parse("stim.raw")
    measurements, waveform_info_list, sessions, programs, items = parser.parse('10HzStim.raw')
    #        measurements, waveform_info_list, sessions, programs, items = parser.parse('stim.raw')
    print(f'Number of Measurement blocks: {len(measurements)}')
    num_points = list()
    for m in measurements:
        num_points.append(len(m.ch1))
    print(Counter(num_points))
    print(f'Number of waveform info blocks: {len(waveform_info_list)}')
    print(f'Number of  Sessions: {len(sessions)}')
    for session in sessions:
        print(textwrap.indent(f'{session}', "   "))
    print(f'Number of programs: {len(programs)}')
    for p in programs:
        print(p)

