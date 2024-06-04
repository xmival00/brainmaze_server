"""
This file contains classes that reflect the SLOT and STIM_PROGRAM structs found in the ALCP rev 3 defined
(in that document) as follows:

#define MAX_NUM_OF_SLOTS                            (8)
#define PROGRAM_DESCRIPTION_LEN                     (32)

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

typedef struct {
      UCHAR Description[ PROGRAM_DESCRIPTION_LEN ];

      UINT8 PatientSelectable             : 1;
      UINT8 PatientDecrementLimit         : 4;
      UINT8 StimulationWaveforms          : 3;

      UINT8 OutputVoltage                 : 4;
      UINT8 PatientAllowedAdjustment      : 1;
      UINT8 _filler1                      : 3;

      SLOT Slots[MAX_NUM_OF_SLOTS ];
} STIM_PROGRAM;
"""

import bitstring
import textwrap
from .slot import Slot
from .parser_exceptions import InvalidStimProgramSizeException
from .parser_utils import unpack_bits

PROG_DESC_N_BYTES = 32 # 32 uchar (byte) values
NUM_SLOTS     = 8

SLOT_ARRAY_SIZE = Slot.SLOT_SIZE * NUM_SLOTS
STIM_PROGRAM_N_BYTES = PROG_DESC_N_BYTES + 1 + 1 + SLOT_ARRAY_SIZE

class StimProgram():
    def __init__(self, program_bytes:bytearray):
        if len(program_bytes) != STIM_PROGRAM_N_BYTES:
            raise InvalidStimProgramSizeException(f'Attempt to create a StimProgram with {len(program_bytes)} bytes. StimProgram requires exactly {STIM_PROGRAM_N_BYTES} bytes')

        # First 32 bytes are a string description
        self.description = program_bytes[:32].decode('utf-8').rstrip("\0")

        # Bytes 32 and 33 are a two byte packed struct
        self.patient_selectable = bool(unpack_bits(program_bytes[32], 0, 1))
        self.patient_decrement_limit = unpack_bits(program_bytes[32], 1, 4)
        self.stim_waveforms = unpack_bits(program_bytes[32], 5, 3)

        self.output_voltage = unpack_bits(program_bytes[33], 0, 4)
        self.patient_allowed_adj = bool(unpack_bits(program_bytes[33], 4, 1))

        # Bytes from 34 on are slots
        self.slots = []
        slot_index = 34
        for i in range(8):
            self.slots.append(Slot(program_bytes[slot_index:slot_index+Slot.SLOT_SIZE]))
            slot_index += Slot.SLOT_SIZE

    @property
    def num_bytes(self):
        return STIM_PROGRAM_N_BYTES

    def __str__(self):
        result = f'Program Description: {self.description}\n'
        result += f'Patient Selectable: {_decode_patient_selectable(self.patient_selectable)} ({self.patient_selectable})\n'
        result += f'Patient Decrement Limit: {_decode_patient_decrement_limit(self.patient_decrement_limit)} ({self.patient_decrement_limit})\n'
        result += f'Stim Waveforms: {_decode_stim_waveforms(self.stim_waveforms)} ({self.stim_waveforms})\n'
        result += f'Output Voltage: {_decode_output_voltage(self.output_voltage)} ({self.output_voltage})\n'
        result += f'Patient Allowed Adjust: {self.patient_allowed_adj}\n'
        for i in range(len(self.slots)):
            result += f'   Slot {i}\n'
            slot_string = f'{self.slots[i]}'
            result += textwrap.indent(slot_string, '      ') + '\n'
        return result


def _decode_patient_selectable(value: bool) -> str:
    if (value):
        return 'Yes'
    return 'No'

def _decode_patient_decrement_limit(value:int) -> int:
    return value + 1

def _decode_stim_waveforms(value:int) -> int:
    return value + 1

def _decode_output_voltage(value: int) -> str:
    if value == 0:
        return 'Battery'
    if value == 13:
        return 'Auto'
    return str(value + 4)

def _decode_patient_allowed_adj(value:bool) -> str:
    if value:
        return 'Enabled'
    return 'Disabled'


