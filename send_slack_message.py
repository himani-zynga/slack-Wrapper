import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from exit_codes import ResponseCodes

class send_message :
    env_path = Path(".") / '.env'
    load_dotenv(dotenv_path=env_path)
    _client = None

    def __init__(self):
        self.create_connection()

    def create_connection(self):
        print("step 1")
        self._client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

        response = self._client.api_test()
        if response["ok"]:
            print("Slack client: Connected")
        else:
            print("Slack API Test Failed! Response:", response)

    def send_custom_slack_message(self, formatted_message, channels):
        response_message = {}
        success_slack_channels = ""
        failure_slack_channel = ""
        error_code = ""
        for channel in channels.split(','):
            channel = channel.strip()
            sendCustomSlackMessage = SendCustomSlackMessageClass(channel, formatted_message)
            message = sendCustomSlackMessage.get_message()
            try:
                response = self._client.chat_postMessage(**message)
                if "success_message" not in response_message:
                    response_message["success_message"] = ""
                success_slack_channels+=channel+", "
                
            except Exception as e:
                print(f"Failed to send message to channel {channel}: {e}.\n")
                error=f"{e}"
                failure_slack_channel+=channel+", "
                if "channel_not_found" in error:
                    error_code = ResponseCodes.CHANNEL_NOT_FOUND
                if "invalid_blocks_format" in error:
                    error_code = ResponseCodes.INVALID_MESSAGE_FORMAT
                if "error_code" and "error_message" not in response_message:
                    response_message["error_code"] = ""
                    response_message["error_message"] = ""                
                continue

        if "success_message" in response_message:
            success_slack_channels = success_slack_channels[:-2]
            response_message["success_message"]= f"Successfully sent slack message to channel {success_slack_channels}."
        if "error_message" in response_message:
            failure_slack_channel = failure_slack_channel[:-2]
            response_message["error_message"] = f"Failed to send slack message to channel {failure_slack_channel}."
        if error_code == "":
            error_code = ResponseCodes.SUCCESS

        response_message["error_code"]= f"{error_code.value}"
        return response_message
        
    @property
    def slack_client(self):
        return self._client

class SendCustomSlackMessageClass:
    
    def __init__(self, channel, formatted_message):
        self.channel = channel
        self.timestamp = ''
        self.formatted_message = formatted_message
        self.did_build_fail = ("fail" in formatted_message or "FAIL" in formatted_message)

        if self.did_build_fail:
            self.icon_emoji = ":ash-not-impressed:"
        else:
            self.icon_emoji = ":ash-impressed:"

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Release Mate',
            'icon_emoji': self.icon_emoji,
            'blocks': self.formatted_message
        }


SEND_MESSAGE = send_message()
