import struct
import textwrap
from enum import Enum

from .scan_channel_config import ScanChannelConfig
from .parser_exceptions import InvalidIndexValueException
from .parser_utils import unpack_bits
class SessionType(Enum):
    SCAN = 0
    FIXED = 1


class RecordingSession:
    RECORDING_SESSION_N_BYTES = 8 + ScanChannelConfig.SCAN_CHANNEL_CONFIG_N_BYTES * 8

    def __init__(self, data_block:bytearray, end_index):
        recording_session_bytes = data_block[end_index - RecordingSession.RECORDING_SESSION_N_BYTES: end_index]

        # The first 8 bytes are 4 UINT16 values, the first of which is packed. Use struct.unpack to properly handle
        # the endienness of the UINT16 values
        packed_values, scan_interval_duration, scan_retrigger_interval, scan_stim_off_duration = struct.unpack('<4H', recording_session_bytes[:8])
        self.patient_selectable = bool(unpack_bits(packed_values, 0, 1))
        self.type = SessionType(unpack_bits(packed_values, 1, 1))

        self.sampling_freq_index = unpack_bits(packed_values, 2, 2)
        if self.sampling_freq_index > 2:
            raise InvalidIndexValueException("Sampling frequency index out of range")
        self.sampling_freq = [500, 2000, 8000][self.sampling_freq_index]

        self.duration_index = unpack_bits(packed_values, 4, 6)
        self.duration = _duration_index_to_value(self.duration_index)
        self.scan_intervals = unpack_bits(packed_values, 10, 4)

        self.scan_interval_duration = scan_interval_duration
        self.scan_retrigger_interval = scan_retrigger_interval
        self.scan_stim_off_duration = scan_stim_off_duration

        self.scan_channel_configs = list()
        byte_index = 8
        for i in range(8):
            self.scan_channel_configs.append(ScanChannelConfig(recording_session_bytes[byte_index:byte_index+ScanChannelConfig.SCAN_CHANNEL_CONFIG_N_BYTES]))
            byte_index += ScanChannelConfig.SCAN_CHANNEL_CONFIG_N_BYTES

    @property
    def num_bytes(self):
        return RecordingSession.RECORDING_SESSION_N_BYTES

    def __str__(self):
        result =  f'Patient Selectable: {self.patient_selectable}\n'
        result += f'Type: {self.type.name}\n'
        result += f'Sampling Frequency: {self.sampling_freq}\n'
        result += f'Duration: {self.duration} minutes\n'
        result += f'Scan Intervals: {self.scan_intervals}\n'
        result += f'Scan Interval Duration: {self.scan_interval_duration}\n'
        result += f'Scan Retrigger Interval: {self.scan_retrigger_interval}\n'
        result += f'Scan Stim Off Duration: {self.scan_stim_off_duration}\n'
        result += f'Scan Channel Configs:\n'
        for scan_chan_config in self.scan_channel_configs:
            result += textwrap.indent(f'{scan_chan_config}\n', '   ')
        return result

def _duration_index_to_value(index):
    """ Convert duration index to duration in minutes"""
    if index > 48:
        raise InvalidIndexValueException("Duration index out of range")
    if index <= 8:
        return index+1
    if index <= 13:
        return (index - 8) * 10
    return (index - 13) * 60