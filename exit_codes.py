from enum import Enum

class ResponseCodes(Enum):
    SUCCESS = 0
    CHANNEL_NOT_FOUND = 1
    INVALID_MESSAGE_FORMAT = 2
    INVALID_TEMPLATE_PATH = 3
