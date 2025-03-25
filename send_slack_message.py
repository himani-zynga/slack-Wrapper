import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from exit_codes import ResponseCodes
from response_constants import ResponseConstansts


class SlackMessageSender:
    env_path = Path(".") / '.env'
    load_dotenv(dotenv_path=env_path)

    def __init__(self):
        self._client = None
        self.create_connection()

    def create_connection(self):
        print("Step 1: Creating Slack connection.")
        self._client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
        response = self._client.api_test()
        if response.get("ok"):
            print("Slack client: Connected")
        else:
            print("Slack API Test Failed! Response:", response)

    # Sends a formatted message to specified Slack channels.
    def send_slack_message(self, formatted_message, channels):
        response_message = {}
        success_channels = ""
        failure_channels = ""

        for channel in channels.split(','):
            channel = channel.strip()
            message = self.create_message(channel, formatted_message)
            
            try:
                response = self._client.chat_postMessage(**message)
                success_channels += channel + ", "
            except Exception as e:
                print(f"Failed to send message to channel {channel}: {e}.\n")
                failure_channels += channel + ", "
                error_code = self.process_error(e, response_message)
                continue

        # Finalize the success and error message
        response_message = self.finalize_message(response_message, success_channels, failure_channels)
        return response_message

    # Creates a message structure for Slack.
    def create_message(self, channel, formatted_message):
        icon_emoji = ":ash-impressed:" if "fail" not in formatted_message or "FAIL" not in formatted_message else ":ash-not-impressed:"
        return {
            'channel': channel,
            'username': 'Release Mate',
            'icon_emoji': icon_emoji,
            'blocks': formatted_message
        }

    # Processes errors and determines the corresponding error code.
    def process_error(self, error, response_message):
        error_message = str(error)
        error_code = ""

        if "channel_not_found" in error_message:
            error_code = ResponseCodes.CHANNEL_NOT_FOUND
        elif "invalid_blocks_format" in error_message:
            error_code = ResponseCodes.INVALID_MESSAGE_FORMAT
        else:
            error_code = ResponseCodes.UNKNOWN_ERROR

        # Set error code and error message in response_message
        response_message[ResponseConstansts.ERROR_CODE.value] = error_code.value
        response_message[ResponseConstansts.ERROR_MESSAGE.value] = error_code.name
        return error_code

    # Finalizes the success and error messages.
    def finalize_message(self, response_message, success_channels, failure_channels):
        if success_channels:
            response_message[ResponseConstansts.SUCCESS_MESSAGE.value] = f"Successfully sent Slack message to channel(s) {success_channels[:-2]}."
        if failure_channels:
            response_message[ResponseConstansts.FAILURE_MESSAGE.value] = f"Failed to send Slack message to channel(s) {failure_channels[:-2]}."

        if ResponseConstansts.ERROR_CODE.value not in response_message:
            response_message[ResponseConstansts.ERROR_CODE.value] = ResponseCodes.SUCCESS.value

        return response_message

    @property
    def slack_client(self):
        return self._client

SEND_MESSAGE = SlackMessageSender()
