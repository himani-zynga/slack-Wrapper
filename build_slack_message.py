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
        
    def create_dict_msg_template_params(self, msg_template_params):
        template_input_array = list(msg_template_params.keys())
        return template_input_array
    
    def extract_placeholders(self, element, template_params):
        if isinstance(element, str):
            placeholders = re.findall(r'{(.*?)}', element)
            template_params.extend(placeholders)
    
    def create_template_params(self, template):
        template_params = []
        self.extract_placeholders(template, template_params)
        return template_params
    
    def replace_template_params(self, template, msg_template_params, response_message):

        placeholders = re.findall(r'{(.*?)}', template)
        
        for placeholder in placeholders:
            if placeholder in msg_template_params:
                template = template.replace(f'{{{placeholder}}}', msg_template_params[placeholder])
            else:
                template = template.replace(f'{{{placeholder}}}', f'{{{placeholder}}}')  # Keep the placeholder if no value is found
                error_code = ResponseCodes.PARAMETER_NOT_FOUND
                response_message['error_code'] = error_code.value
                response_message['error_message'] = error_code.name
        
        return template

    def create_message_block(self, template, msg_template_params, response_message):
        # iterate over msg_template_params and get each key and search for each key in template and do string replacement there
        dict_msg_template_params = self.create_dict_msg_template_params(msg_template_params)
        template_params = self.create_template_params(template)

        if(len(dict_msg_template_params)<len(template_params)):
            error_code = ResponseCodes.INSUFFICIENT_PARAMETERS
            response_message['error_code'] = error_code.value
            response_message['error_message'] = error_code.name
            return response_message
        else:
            template = self.replace_template_params(template, msg_template_params, response_message)

        if isinstance(template, str):
            try:
                template_data = json.loads(template)
            except json.JSONDecodeError:
                raise Exception("Error: Template is not a valid JSON string")
        else:
            template_data = template
            
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
