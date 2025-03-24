from exit_codes import ResponseCodes
import os
import json
import re

class build_message:

    def create_path(self, job_name, state):
        template_path = 'Templates/'+job_name+'/'+state+".txt"
        return template_path
    
    def does_template_exist(self, job_name, state):
        template_path = self.create_path(job_name, state)
        return os.path.exists(template_path)
        
    def get_template(self, job_name, state):
        template_path = self.create_path(job_name, state)
        try:
            with open(template_path, "r") as file:
                template = file.read()
                return template
        except Exception as e:
            raise Exception(f"Error : {e}")
    
    def replace_template_params(self, template, msg_template_params, response_message):

        placeholders = re.findall(r'\${(.*?)}', template)

        for placeholder in placeholders:
            # Check for case-insensitive match in msg_template_params
            matched_placeholder = next((key for key in msg_template_params if key.lower() == placeholder.lower()), None)
            
            if matched_placeholder:
                # If the placeholder is found, replace it with the corresponding value
                template = re.sub(f'\\${{{re.escape(placeholder)}}}', msg_template_params[matched_placeholder], template, flags=re.IGNORECASE)
            else:
                template = re.sub(f'\\${{{re.escape(placeholder)}}}', f'${{{placeholder}}}', template, flags=re.IGNORECASE)
                error_code = ResponseCodes.INSUFFICIENT_PARAMETERS
                response_message['error_code'] = error_code.value
                response_message['error_message'] = error_code.name
        
        return template

    def create_message_block(self, template, msg_template_params, response_message):
        template = self.replace_template_params(template, msg_template_params, response_message)

        if isinstance(template, str):
            try:
                template_data = json.loads(template)
            except json.JSONDecodeError:
                raise Exception("Error: Template is not a valid JSON string")
        else:
            template_data = template

        if 'error_code' not in response_message:
            error_code = ResponseCodes.SUCCESS
            response_message['error_code'] = error_code.value
            
        response_message['formatted_msg'] = template_data

        return response_message

    def build_custom_slack_message(self, job_state_info, msg_template_params, msg_attachments):
        response_message = {}
        error_code = ""
        job_name = job_state_info['job_name']
        state = job_state_info['state']

        if self.does_template_exist(job_name, state) == False:
            error_code = ResponseCodes.INVALID_TEMPLATE_PATH
            response_message['error_code'] = error_code.value
            response_message['error_message'] = error_code.name
        else:
            template = self.get_template(job_name, state)
            response_message = self.create_message_block(template, msg_template_params, response_message)

        return response_message
    
    

BUILD_MESSAGE = build_message()
