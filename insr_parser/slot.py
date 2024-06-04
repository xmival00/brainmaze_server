"""
This file contains classes that reflect the SLOT struct found in the ALCP rev 3 defined
(in that document) as follows:

typedef struct {
      UINT16           WaveformInstance      : 4;
      UINT16           SlotWidth             : 7;
      UINT16           DutyCycle             : 1;
      UINT16           _filler1              : 4;

      UINT16           Decimate;
      UINT16           OnFrames;
      UINT16           OffFrames;
      UINT16           Ramp;
} SLOT;
"""

import struct
from .parser_utils import unpack_bits
from .parser_exceptions import InvalidSlotSizeException
class Slot:
    SLOT_SIZE = 10 # one packed UINT16 + 4 UINT16

    def __init__(self, slot_bytes : bytearray):
        if len(slot_bytes) != Slot.SLOT_SIZE:
            raise InvalidSlotSizeException()

        # the slot is represented as 5 UINT16 values (the first of which is packed). In order to handle
        # endienness we use struct.unpack to get the 5 values
        packed_values, decimation, on_frames, off_frames, ramp = struct.unpack('<5H', slot_bytes)

        self.waveform_instance_index = unpack_bits(packed_values, 0, 4)
        self.waveform_instance = self.waveform_instance_index + 1

        self.slot_width_index = unpack_bits(packed_values, 4, 7)
        self.slot_width = _slot_width_index_to_value(self.slot_width_index)

        self.duty_cycle = bool(unpack_bits(packed_values, 11, 1))

        self.decimation = decimation
        self.on_frames = on_frames
        self.off_frames = off_frames
        self.ramp = ramp

    def __str__(self):
        result = f'Waveform Instance: {self.waveform_instance} \n'
        result += f'Slot Width: {self.slot_width * 1000} ms\n'
        result += f'Duty Cycle: {_decode_duty_cycle(self.duty_cycle)} ({self.duty_cycle})\n'
        result += f'Decimation: {self.decimation}\n'
        result += f'On Frames: {self.on_frames}\n'
        result += f'Off Frames: {self.off_frames}\n'
        result += f'Ramp: {_decode_ramp(self.ramp)} '
        return result


def _slot_width_index_to_value(index: int) -> float:
    if index < 56:
        return index * .000125 + .003
    return (index - 56) * .050


def _decode_duty_cycle(value: bool) -> str:
    if value:
        return 'Yes'
    return 'No'

def _decode_ramp(value: int) -> str:
    if value == 0:
        return 'Disabled'
    return str(value)
