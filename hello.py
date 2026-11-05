import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def join_channel(channel_id):
    """Try to add the bot to a public channel."""
    try:
        client.conversations_join(channel=channel_id)
        print("Bot joined the channel.")
        return True
    except SlackApiError as e:
        error = e.response["error"]
        if error == "method_not_supported_for_channel_type":
            print("This is a private channel. Run /invite @YourBot in it.")
        else:
            print("Could not join:", error)
        return False


def post_hello(channel, name):
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=f"Hello from {name}",
        )
        print("Posted OK, message timestamp:", response["ts"])
    except SlackApiError as e:
        error = e.response["error"]
        if error == "not_in_channel":
            print("The bot is not in that channel. Invite it first.")
        else:
            print("Slack rejected the request:", error)


channel_id = os.environ.get("TEST_CHANNEL_ID")
if channel_id:
    join_channel(channel_id)
    post_hello(channel_id, "Lavanya")

post_hello("#slack-training", "Lavanya")
post_hello("#no-such-channel-xyz", "Lavanya")