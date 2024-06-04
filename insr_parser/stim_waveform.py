from enum import Enum
from .parser_exceptions import InvalidWaveformIndexValueException
from .parser_utils import unpack_bits, amplitude_index_to_volts

class ElectrodeType(Enum):
    OFF = 0
    ANODE = 1
    CATHODE = 2


class StimWaveform:
    STIM_WAVEFORM_N_BYTES = 7
    def __init__(self, program_info_bytes:bytearray, index):
        """
        Create an instance of a StimWaveform

        """
        stim_waveform_bytes = program_info_bytes[index:index+StimWaveform.STIM_WAVEFORM_N_BYTES]

        burst = bool(unpack_bits(stim_waveform_bytes[0],0,1))
        self.burst = bool(burst)

        burst_index = unpack_bits(stim_waveform_bytes[0], 1, 4)
        self.burst_count = burst_index + 2

        burst_period_index = unpack_bits(stim_waveform_bytes[0], 5, 3)
        self.burst_period = _burst_period_index_to_seconds(burst_period_index)

        amplitude_index = unpack_bits(stim_waveform_bytes[1], 0, 6)
        self.waveform_amplitude = amplitude_index_to_volts(amplitude_index)

        self.amplitude_ratio = unpack_bits(stim_waveform_bytes[1], 6, 2)

        width_index = unpack_bits(stim_waveform_bytes[2], 0, 4)
        self.waveform_width = _waveform_width_index_to_seconds(width_index)

        self.terminals = []
        for terminal_byte in [3, 4, 5, 6]:
            for i in range(4):
                terminal_value = unpack_bits(stim_waveform_bytes[terminal_byte], i*2, 2)
                self.terminals.append(ElectrodeType(terminal_value))

    @property
    def num_bytes(self):
        return StimWaveform.STIM_WAVEFORM_N_BYTES

    def __str__(self):
        result = f'Burst: {self.burst}\n'
        result += f'Burst Count: {self.burst_count}\n'
        result += f'Burst Period: {self.burst_period * 1000} ms\n'
        result += f'Waveform Amplitude {self.waveform_amplitude * 1000} ma\n'
        result += f'Amplitude Ratio: {self.amplitude_ratio}\n'
        result += f'Waveform Width: {self.waveform_width * 1e6} us\n'
        for i in range(16):
            result += f'Terminal {i+1}: {self.terminals[i]}\n'
        return result


def _burst_period_index_to_seconds(index:int) -> float:
    """

    Args:
        index:

    Returns:

    """
    if index <0 or index > 6:
        raise InvalidWaveformIndexValueException
    period = (index * .5 + 2) / 1000.0
    return period



def _waveform_width_index_to_seconds(index: int) -> float:
    """Convert a waveform width index to waveform width in seconds"""
    if index < 0 or index > 14:
        raise InvalidWaveformIndexValueException
    return (index + 2)/32000