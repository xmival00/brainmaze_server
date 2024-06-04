import numpy as np
from .parser_exceptions import InvalidMeasurementBlocSizeException, ParserException
class Measurement:
    OVERHEAD_BYTES = 5 # 1 byte for type, 4 bytes for num measurements
    def __init__(self, data_block:bytearray, end_index):
        # The end index should be pointing at the record type, which should be a zero
        self.record_type = data_block[end_index]
        if self.record_type != 0:
            raise ParserException(f'Attempt to create a Measurement but record type of {self.record_type} is not zero')
        # After tne number of measurements is removed, what remains should look like this:
        #  +---------------------------------------+---------------------------------------+-------------+
        #  |             Measurement 1             |             Measurement 2             | ....        |
        #  +---------------------------------------+---------------------------------------+-------------+
        #  | Ch1 MSB | Ch1 LSB | Ch2 MSB | Ch2 LSB | Ch1 MSB | Ch1 LSB | Ch2 MSB | Ch2 LSB | ... etc ... |
        #  +---------------------------------------+---------------------------------------+-------------+
        num_measurements = int.from_bytes(data_block[end_index - 4:end_index], "little")
        self._measurements_n_bytes = num_measurements * 4
        measurement_end_index = end_index - 5  # 1 byte for type, 4 bytes for length
        measurement_start_index = measurement_end_index + 1 - self._measurements_n_bytes

        measurement_values = np.frombuffer(data_block[measurement_start_index: measurement_end_index + 1], dtype='>i2')  # dtype is big-endian 2 byte int
        self._ch1 = measurement_values[0::2]
        self._ch2 = measurement_values[1::2]

    @property
    def num_bytes(self):
        return self._measurements_n_bytes + Measurement.OVERHEAD_BYTES

    @property
    def ch1(self):
        return self._ch1

    @property
    def ch2(self):
        return self._ch2

    @property
    def num_samples(self):
        return len(self.ch1)

    def __str__(self):
        return f'Measurement length: {len(self.ch1)}'
