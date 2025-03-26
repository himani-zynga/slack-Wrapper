from enum import Enum

class ResponseConstant(Enum):
    ERROR_CODE = 'error_code'
    ERROR_MESSAGE = 'error_message'
    FORMATTED_MESSAGE = 'formatted_message'
    JOB_NAME = 'job_name'
    STATE = 'state'
    SUCCESS_MESSAGE = 'success_message'
    FAILURE_MESSAGE = 'failure_message'
    MESSAGE_ID = "message_id"
    MESSAGES = "messages"
    LAST_MODIFIED_TIMESTAMP = "last_modified"
