from binascii import crc_hqx
from .parser_exceptions import CrcFailureException, InvalidWaveformIndexValueException

DEFAULT_CHUNK_SIZE = 2**14
def unpack_bits(value, start_bit, n_bits):
    mask  = (1 << n_bits) - 1
    return (value >> start_bit) & mask

def s16(value):
    """Return a signed version of a 16 bit (signed) value"""
    return -(value & 0x8000) | (value & 0x7fff)


def un_chunk(data, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Process an array of data that was read from a file. Data is in "chunks" that are all of fixed size except for
    the final chunk which may be smaller. Each chunk includes a 2 byte CRC at the end, therefore the CRC of the entire
    chunk (including the CRC bytes) will have a CRC of zero.

    Parameters:
        data: array of bytes that was read from a file

    Returns:
        List of bytes that represent the raw data with CRC bytes removed

    Raises:
        CrcFailureException if crc fails
    """
    #un_chunked_data = list()
    un_chunked_data = bytearray()
    start_index = 0
    data_len= len(data)
    while start_index < data_len:
        bytes_to_process = min(chunk_size, data_len - start_index)
        #crc = crc_hqx(data[:bytes_to_process], 0xffff)
        crc = crc_hqx(data[start_index : start_index + bytes_to_process], 0xffff)
        if crc != 0:
            raise CrcFailureException("CRC check failed")
        #un_chunked_data += list(data[:bytes_to_process - 2])
        un_chunked_data += data[start_index: start_index + bytes_to_process - 2]
        #data = data[bytes_to_process:]
        start_index += bytes_to_process
    return un_chunked_data


def amplitude_index_to_volts(index: int) -> float:
    """Convert an amplitude index to the associated amplitude voltage"""
    if index > 55:
        raise InvalidWaveformIndexValueException
    if index <= 8:
        amplitude = index * .1 + .1
    elif index <= 24:
        amplitude = (index - 9) * .25 + 1
    else:
        amplitude = (index - 25) * .5 + 5
    amplitude = round(amplitude,2)
    return amplitude / 1000.0