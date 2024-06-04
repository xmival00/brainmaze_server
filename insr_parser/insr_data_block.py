from dataclasses import dataclass
from insr_parser.measurement import Measurement
from insr_parser.waveform_info import WaveformInfo
from insr_parser.session_info import SessionInfo
from insr_parser.program_info import ProgramInfo
@dataclass()
class InsrDataBlock():
    measurement_list:list[Measurement]
    waveform_info_list:list[WaveformInfo]
    session_info_list:list[SessionInfo]
    program_info_list:list[ProgramInfo]

    def info(self):
        """"Create a string representation of an InsrDataBlock"""
        # TODO: maybe just rename this to __str__ ??
        result = ''
        result += str(self.session_info_list[0])
        for info in self.program_info_list:
            result += str(info)
        return result