"""
This module provides the InsrParser class which is used to read and parse the data provided by the CCC INSR controller
application based on revision 6 of the ALCP
"""
import struct
from types import MethodType

from .parser_utils import un_chunk
from .parser_exceptions import ParserException
from .waveform_info import WaveformInfo
from .program_info import ProgramInfo
from .session_info import SessionInfo
from .measurement import Measurement



class InsrParser():
    def __init__(self, pct_complete_callback = None, status_msg_callback = None):
        """
        Initialize an instance of the InsrParser class
        Args:
            pct_complete_callback: EITHER a method OR a signal that takes a single int parameter as an argument
            status_msg_callback: EITHER a method OR a signal that takes a single string parameter as an argument
        """
        self.pct_complete_callback = pct_complete_callback
        self.status_message_callback = status_msg_callback

    def parse(self, input_file:str):
        self.update_status_message("Reading data file")
        with open(input_file, mode='rb') as fp:
            raw_data = fp.read()

        # raw data in file is in 16KB chunks (except for last chunk which may be smaller). Each chunk includes a CRC
        # so we need to remove the CRC bytes (and check the CRC while we're at it)
        self.update_status_message("Un-chunking data")
        data = un_chunk(raw_data)
        alcp_rev = data[0]
        timestamp_bytes = data[1:9]
        data = data[9:] # Get rid of rev and timestamp
        # Deep breath. Now...because of the absolutely brilliant way that the data is packed into the byte array,
        # everything has to be parsed from the END of the data backward. The data is packed as multiple record types,
        # and the LAST byte of the record indicates what the type is (from which things like the size of the record can
        # be determined.
        end_index = len(data) -1

        self.waveform_info_list = list()
        self.measurements = list()
        self.session_info_list = list()
        self.program_info_list = list()
        self.item_type_list = list() # To aid in debugging, track which types we get

        ####### For debugging / evaluation only: wrap this in a try/except so that we can just early exit if the data block
        ####### is malformed.
        self.update_status_message("Parsing data block")
        data_length = len(data)
        try:
            while end_index > 0: #
                pct_complete = (1-end_index/data_length) * 100
                self.update_pct_complete(pct_complete)
                record_type = data[end_index]

                if 0 == record_type:  # measurements, or what CCC calls "REC_ENTRY_RECORD"
                    self.item_type_list.append('Measurement')
                    measurement = Measurement(data, end_index)
                    self.measurements.append(measurement)
                    end_index -= measurement.num_bytes

                elif 1 == record_type: # Waveform info
                    self.item_type_list.append('Waveform Info')
                    waveform_info = WaveformInfo(data,end_index)
                    self.waveform_info_list.append(waveform_info)
                    end_index -= waveform_info.num_bytes

                elif 2 == record_type:  # Program Info
                    self.item_type_list.append('Program Info')
                    program_info = ProgramInfo(data, end_index)
                    self.program_info_list.append(program_info)
                    end_index -= program_info.num_bytes

                elif 3 == record_type: # Session Info
                    self.item_type_list.append('Session Info')
                    session_info = SessionInfo(data, end_index)
                    self.session_info_list.append(session_info)
                    end_index -= session_info.num_bytes

                else:
                    raise ParserException(f'Unknown record type {record_type} found in data')
        except ParserException as e:
            print(f'Early exit due to ParserException {type(e)}')
        self.update_pct_complete(100)
        self.update_status_message("Data block parsing complete")
        # Note: the [::-1] is a handy way to reverse a list. Allegedly faster than calling reverse on the list.

        ts, rtc_idx = struct.unpack_from('II', timestamp_bytes)
        return ts, alcp_rev, self.measurements[::-1], self.waveform_info_list[::-1], self.session_info_list, self.program_info_list


    def update_status_message(self, message):
        if self.status_message_callback is not None:
            if isinstance(self.status_message_callback, MethodType):
                self.status_message_callback(message)
            else:
                self.status_message_callback.emit(message)

    def update_pct_complete(self, pct):
        if self.pct_complete_callback is not None:
            if isinstance(self.pct_complete_callback, MethodType):
                self.pct_complete_callback(pct)
            else:
                self.pct_complete_callback.emit(pct)
