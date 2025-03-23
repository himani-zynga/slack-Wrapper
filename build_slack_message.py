from exit_codes import ResponseCodes
import os
import json
import fnmatch

class build_message:

    def create_path(self, job_name, state):
        template_path = 'Templates/'+job_name+'/'+state+".txt"
        return template_path
    
    def does_template_exist(self, job_name, state):
        template_path = self.create_path(job_name, state)
        for file in os.listdir(os.path.dirname('Slack_Wrapper')):
            print(file, "gjhg", template_path)
            if fnmatch.fnmatch(file, template_path):
                return True
            
        print("The template path does not exist.")
        return False
        
    def get_template(self, job_name, state):
        template_path = self.create_path(job_name, state)
        try:
            with open(template_path, "r") as file:
                template = file.read()
                return template
        except Exception as e:
            print(f"Failed to read the file at {template_path}")

    def get_parameter(self, line):
        start = "{"
        end = "}"

        start_index = line.find(start)
        end_index = line.find(end, start_index + len(start))

        if start_index != -1 and end_index != -1:
            parameter = line[start_index + len(start):end_index]
            return parameter
        else:
            print("Delimiters not found")

#         start = text.find("[") + 1
#         end = text.find("]")
#         substring = text[start:end]

    def create_message_block(self, template, msg_template_params, response_message):
        # iterate over msg_template_params and get each key and search for each key in template and do string replacement there
        template_input_params = []
        for i in range(len(template)):
            if "text" in template[i] and "{" in template[i] and "}" in template[i]:
                parameter = self.get_parameter(template[i])
                template_input_params.append(parameter)
        

        if isinstance(template, str):
            try:
                template_data = json.loads(template)
            except json.JSONDecodeError:
                print("Error: Template is not a valid JSON string")
                return
        else:
            template_data = template
        response_message['formatted_msg'] = template_data

        return template

    def build_custom_slack_message(self, job_state_info, msg_template_params, msg_attachments):
        response_message = {}
        error_code = ""
        job_name = job_state_info['job_name']
        state = job_state_info['state']

        if self.does_template_exist(job_name, state) == False:
            error_code = ResponseCodes.INVALID_TEMPLATE_PATH
            response_message['error_code'] = error_code.value
        else:
            template = self.get_template(job_name, state)
            message_block = self.create_message_block(template, msg_template_params, response_message)
            print(msg_attachments)
        return response_message
    
    

BUILD_MESSAGE = build_message()
