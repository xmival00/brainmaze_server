class ParserException(Exception):
    pass

class CrcFailureException(ParserException):
    pass

class InvalidHeaderSizeException(ParserException):
    pass

class InvalidStimProgramSizeException(ParserException):
    pass

class InvalidSlotSizeException(ParserException):
    pass

class InvalidWaveformSizeException(ParserException):
    pass

class InvalidProgramInfoSizeException(ParserException):
    pass

class InvalidStimWaveformSizeException(ParserException):
    pass

class InvalidScanChannelConfigSizeException(ParserException):
    pass

class InvalidRecordingSessionSizeException(ParserException):
    pass

class InvalidSessionInfoSizeException(ParserException):
    pass
class IncompleteEventException(ParserException):
    pass

class InvalidMeasurementBlocSizeException(ParserException):
    pass

class InvalidWaveformIndexValueException(ParserException):
    """Exception indicating that an index in the waveform data is invalid (out of range)"""

class InvalidIndexValueException(ParserException):
    """Exception indicating that an index was not within the allowable range"""