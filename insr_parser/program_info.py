from .stim_waveform import StimWaveform
from .stim_program import StimProgram, STIM_PROGRAM_N_BYTES
import textwrap
class ProgramInfo:
    PROGRAM_INFO_N_BYTES = StimWaveform.STIM_WAVEFORM_N_BYTES * 16 + STIM_PROGRAM_N_BYTES
    def __init__(self, data_block:bytearray, end_index):
        self.event = data_block[end_index]
        program_info_bytes = data_block[end_index - ProgramInfo.PROGRAM_INFO_N_BYTES: end_index]
        self.stim_waveforms = list()
        byte_index = 0
        for i in range(16):
            waveform = StimWaveform(program_info_bytes, byte_index)
            self.stim_waveforms.append(waveform)
            byte_index += waveform.num_bytes
        self.stim_program = StimProgram(program_info_bytes[byte_index: byte_index+STIM_PROGRAM_N_BYTES])



    @property
    def num_bytes(self):
        return ProgramInfo.PROGRAM_INFO_N_BYTES + 1
    def __str__(self):
        indent = 3 * ' '
        result = 'Stimulation Program:\n'
        result += textwrap.indent(f'{self.stim_program}', indent)
        result += 'Stim Waveforms:\n'
        for i in range(len(self.stim_waveforms)):
            result += f'Stim Waveform Index {i}:\n'
            result += textwrap.indent(f'{self.stim_waveforms[i]}\n',indent)

        return result

