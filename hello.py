import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()  # reads the tokens from your .env file

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def post_hello(channel, name):
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=f"Hello from {name}",
        )
        print("Posted OK, message timestamp:", response["ts"])
    except SlackApiError as e:
        print("Slack rejected the request:", e.response["error"])


post_hello("#slack-academy", "Lavanya")
post_hello("#no-such-channel-xyz", "Lavanya")