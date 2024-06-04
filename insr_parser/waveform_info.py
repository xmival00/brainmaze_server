import struct
from .parser_exceptions import ParserException
from .parser_utils import unpack_bits, amplitude_index_to_volts


class WaveformInfo():
    WAVEFORM_INFO_N_BYTES = 5
    def __init__(self, data_block:bytearray, end_index):
        waveform_info_bytes = data_block[end_index - WaveformInfo.WAVEFORM_INFO_N_BYTES + 1: end_index +1]
        # The first 4 bytes are actually packed UINT16 values. Since they're little endien we use struct.unpack
        # to rearrange the bytes properly
        packed1, packed2, event = struct.unpack("<HHB",waveform_info_bytes)
        if event != 1:
            raise ParserException(f'Attempt to create WaveformInfo but event {event} is not 1')
        self.event = event

        self.waveform_index = unpack_bits(packed1, 0, 4)
        self.waveform_instance = self.waveform_index + 1

        self.amplitude_index = unpack_bits(packed1, 4, 6)
        self.amplitude = amplitude_index_to_volts(self.amplitude_index)

        self.inhibited_pulse = bool(unpack_bits(packed1, 10, 1))

        left_interval_low = unpack_bits(packed1, 11, 5)
        left_interval_high = unpack_bits(packed2, 0, 2)
        self.left_interval_ticks = left_interval_high << 5 | left_interval_low
        self.left_interval = self.left_interval_ticks * 1/32000

        self.right_interval_ticks = unpack_bits(packed2, 2, 14)
        self.right_interval = self.right_interval_ticks * 1/32000

    @property
    def num_bytes(self):
        return WaveformInfo.WAVEFORM_INFO_N_BYTES

    def __str__(self):
        result = f'Waveform Instance: {self.waveform_instance}\n'
        result += f'Amplitude : {self.amplitude * 1e3} mA\n'
        result += f'Inhibited Pulse: {self.inhibited_pulse}\n'
        result += f'Left Interval: {self.left_interval * 1e6} \u03BCs\n'
        result += f'Right Interval: {self.right_interval * 1e6} \u03BCs'
        return result

