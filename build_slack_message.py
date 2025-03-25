from exit_codes import ResponseCodes
import os
import json
import re
from response_constants import ResponseConstansts

class build_message:

    # Creates the path to the template file based on job name and state
    def create_path(self, job_name, state):
        template_path = 'Templates/'+job_name+'/'+state+".txt"
        return template_path
    
    # Checks if the template file exists at the generated path
    def does_template_exist(self, job_name, state):
        template_path = self.create_path(job_name, state)
        return os.path.exists(template_path)

    # Reads the template content from the file if it exists    
    def get_template(self, job_name, state):
        template_path = self.create_path(job_name, state)
        try:
            with open(template_path, "r") as file:
                template = file.read()
                return template
        except Exception as e:
            raise Exception(f"Error : {e}")
    
    # Replaces placeholders in the template with corresponding values from msg_template_params
    def replace_template_params(self, template, msg_template_params):
        response={}

        # Convert all keys in msg_template_params to lowercase for case-insensitive matching
        msg_template_params_lowercase = {key.lower(): value for key, value in msg_template_params.items()}

        # Find all placeholders in the template in the form of ${placeholder}
        placeholders = re.findall(r'\${(.*?)}', template)

        for placeholder in placeholders:
            matched_placeholder = msg_template_params_lowercase.get(placeholder.lower())

            if matched_placeholder:
                # If a match is found, replace the placeholder with the value from msg_template_params_lowercase
                template = re.sub(f'\\${{{re.escape(placeholder)}}}', matched_placeholder, template, flags=re.IGNORECASE)
            else:
                # If no match is found, add an error message
                error_code = ResponseCodes.INSUFFICIENT_PARAMETERS
                response[ResponseConstansts.ERROR_MESSAGE.value] = error_code.name

        # Store the modified template (with replaced placeholders) in the response
        response[ResponseConstansts.FORMATTED_MESSAGE.value] = template

        return response
    
    # Creates the final response message including error or success codes and formatted template
    def create_response_message(self, response, response_message):
        if ResponseConstansts.ERROR_MESSAGE.value not in response:
            error_code = ResponseCodes.SUCCESS
            response_message[ResponseConstansts.ERROR_CODE.value] = error_code.value
        else:
            response_message[ResponseConstansts.ERROR_CODE.value] = ResponseCodes.INSUFFICIENT_PARAMETERS.value
            response_message[ResponseConstansts.ERROR_MESSAGE.value] = ResponseCodes.INSUFFICIENT_PARAMETERS.name

        template = response[ResponseConstansts.FORMATTED_MESSAGE.value]

        if isinstance(template, str):
            try:
                template_data = json.loads(template)
            except json.JSONDecodeError:
                raise Exception("Error: Template is not a valid JSON string")
        else:
            template_data = template
        
        response_message[ResponseConstansts.FORMATTED_MESSAGE.value] = template_data

        return response_message
    
    # Creates a message block by replacing placeholders in the template and generating the final response
    def create_message_block(self, template, msg_template_params, response_message):
        response = self.replace_template_params(template, msg_template_params)
        response_message = self.create_response_message(response, response_message)
        return response_message


    def build_custom_slack_message(self, job_state_info, msg_template_params, msg_attachments):
        response_message = {}
        error_code = ""

        job_name = job_state_info[ResponseConstansts.JOB_NAME.value]
        state = job_state_info[ResponseConstansts.STATE.value]

        if self.does_template_exist(job_name, state) == False:
            # Check if the template exists, if not, return an error
            error_code = ResponseCodes.INVALID_TEMPLATE_PATH
            response_message[ResponseConstansts.ERROR_CODE.value] = error_code.value
            response_message[ResponseConstansts.ERROR_MESSAGE.value] = error_code.name
        else:
            # If the template exists, read it and create the message block
            template = self.get_template(job_name, state)
            response_message = self.create_message_block(template, msg_template_params, response_message)

        return response_message
    
    

BUILD_MESSAGE = build_message()
