from .parser_utils import unpack_bits
from .parser_exceptions import InvalidScanChannelConfigSizeException

class ScanChannelConfig:
    SCAN_CHANNEL_CONFIG_N_BYTES = 2
    def __init__(self, scan_channel_config_bytes:bytearray):
        if len(scan_channel_config_bytes) != ScanChannelConfig.SCAN_CHANNEL_CONFIG_N_BYTES:
            raise InvalidScanChannelConfigSizeException

        self.chan1_terminal1 = unpack_bits(scan_channel_config_bytes[0], 0, 4)
        self.chan1_terminal2 = unpack_bits(scan_channel_config_bytes[0], 4, 4)

        self.chan2_terminal1 = unpack_bits(scan_channel_config_bytes[1], 0, 4)
        self.chan2_terminal2 = unpack_bits(scan_channel_config_bytes[1], 4, 4)

    def __str__(self):
        result = f'Chan 1 Terminal 1: {self.chan1_terminal1}\n'
        result += f'Chan 1 Terminal 2: {self.chan1_terminal2}\n'
        result += f'Chan 2 Terminal 1: {self.chan2_terminal1}\n'
        result += f'Chan 2 Terminal 2: {self.chan2_terminal2}\n'
        return result
