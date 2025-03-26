from exit_codes import ResponseCodes
import os
import json
from response_constants import ResponseConstant
import datetime

class SaveSlackMessage:
    # Create a path for the message file.
    def create_path(self, message_id):
        message_id = message_id.lower()
        message_path = "Messages/"+message_id+".json"
        return message_path
    
    # Returns the current time as a string.
    def get_current_time(self):
        return int(datetime.datetime.now().timestamp())
    
    # Update the existing message file with new content by appending new_message along with divider and update time.
    def update_message(self, message_path, formatted_message, message_id):
        try:
            with open(message_path, 'r') as data:
                file = json.load(data)
            if not file:
                return self.get_new_message_file_content(formatted_message, message_id)
        except Exception as e:
            raise Exception(f"Error : {e}")
        
        divider_block = self.divider_template()
        formatted_time = self.get_current_time()

        file[ResponseConstant.MESSAGES.value].append(divider_block)
        file[ResponseConstant.MESSAGES.value].extend(formatted_message)
        file[ResponseConstant.LAST_MODIFIED_TIMESTAMP.value] = f"{formatted_time}"

        return file

    def divider_template(self):
        block={
            "type": "divider"
        }
        return block
    
    # Creates new content for a message when no file exists.
    def get_new_message_file_content(self, formatted_message, message_id):
        content = {}
        formatted_time = self.get_current_time()
        content[ResponseConstant.MESSAGE_ID.value] = f"{message_id}"
        content[ResponseConstant.MESSAGES.value] = formatted_message
        content[ResponseConstant.LAST_MODIFIED_TIMESTAMP.value] = f"{formatted_time}"
        return content
    
    # Returns the message content that has to be written in the file.
    def get_message_file_content(self, message_path, formatted_message, message_id):
        if os.path.exists(message_path):
            return self.update_message(message_path, formatted_message, message_id)
        else:
            return self.get_new_message_file_content(formatted_message, message_id)

    def is_valid_formatted_message(self, formatted_message):
        if isinstance(formatted_message, list):
            for item in formatted_message:
                if not isinstance(item, dict):
                    return False
            return True
        return False

    def save_slack_message(self, formatted_message, message_id):
        error_code = ""
        response_message = {}
        if self.is_valid_formatted_message(formatted_message) and isinstance(message_id, str):
            # check for array of json (jsons)
            message_path = self.create_path(message_id)
            modified_content = self.get_message_file_content(message_path, formatted_message, message_id)
            try:    
                with open(message_path, 'w') as f:
                    json.dump(modified_content, f, indent=4)
            except Exception as e:
                raise Exception(f"Error : {e}")

            error_code = ResponseCodes.SUCCESS
            response_message[ResponseConstant.ERROR_CODE.value] = error_code.value

        else:
            error_code = ResponseCodes.INVALID_INPUT
            response_message[ResponseConstant.ERROR_CODE.value] = error_code.value
            response_message[ResponseConstant.ERROR_MESSAGE.value] = error_code.name

        return response_message



SAVE_MESSAGE = SaveSlackMessage() 
