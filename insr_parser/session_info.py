from .recording_session import RecordingSession
from .parser_exceptions import ParserException
class SessionInfo:
    SESSION_INFO_N_BYTES = RecordingSession.RECORDING_SESSION_N_BYTES + 1
    def __init__(self, data_block:bytearray, end_index:int):
        self.event = data_block[end_index]
        if self.event != 3:
            raise ParserException(f'Attempt to create SessionInfo but event {self.event} is not 3')
        self.recording_session = RecordingSession(data_block, end_index)

    @property
    def num_bytes(self):
        return self.recording_session.num_bytes + 1
    def __str__(self):
        return str(self.recording_session)