from flask import Flask, Response, jsonify, request, abort
from send_slack_message import SEND_MESSAGE
from build_slack_message import BUILD_MESSAGE
from pathlib import Path
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

import werkzeug.exceptions as ex
import atexit
import os
import os.path
import ssl
import sys

sys.stderr = open('/dev/null')       # Silence silly warnings from paramiko
sys.stderr = sys.__stderr__

ssl._create_default_https_context = ssl._create_unverified_context
env_path = Path(".") / '.env'
load_dotenv(dotenv_path=env_path)
app = Flask(__name__)

def get_arguments(request):
    data = request.get_json()
    return data

@app.route('/slack/send_messsage', methods = ['POST'])
def sendCustomSlackMessage():
    data = get_arguments(request)
    formatted_message = data['formatted_message']
    channels = data['channels']

    try:
        response_message = SEND_MESSAGE.send_custom_slack_message(formatted_message, channels)
    
    except Exception as e:
        print (e)
        response_message = f"Failed to send slack message. Error: {e}"

    return response_message

@app.route('/slack/build_message', methods = ['POST'])
def buildFormattedMessage():
    data = get_arguments(request)
    job_state_info = data['job_state_info']
    msg_template_params = data['msg_template_params']
    msg_attachments = data.get('msg_attachments')

    try:
        response_message = BUILD_MESSAGE.build_custom_slack_message(job_state_info, msg_template_params, msg_attachments)

    except Exception as e:
        response_message = f"Error: {e}"
    
    return response_message


print("step 2")
scheduler = BackgroundScheduler()
# scheduler.add_job(func=machine_memory_check, trigger="interval", seconds=300)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    port = os.environ.get('FLASK_SERVER_PORT', 3000)
    app.run(host='0.0.0.0', port=int(port))
    # app.run(host='0.0.0.0', port=os.environ('FLASK_SERVER_PORT'))
