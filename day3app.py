import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])
NEW_HIRES_CHANNEL_ID = os.environ["NEW_HIRES_CHANNEL_ID"]

CHECKLIST = (
    "Welcome to the team! Your onboarding checklist:\n"
    "1. Introduce yourself in #new-hires\n"
    "2. Read the pinned messages in #slack-training\n"
    "3. Set up your profile photo and time zone\n"
    "4. Ask your buddy any questions"
)


@app.event("member_joined_channel")
def welcome_new_member(event, client, context):
    if event["channel"] != NEW_HIRES_CHANNEL_ID:
        return
    user_id = event["user"]
    if user_id == context.bot_user_id:
        return  # ignore the bot joining the channel itself
    try:
        client.chat_postMessage(channel=user_id, text=CHECKLIST)
        print("Welcome DM sent")
    except SlackApiError as e:
        print("Could not send DM:", e.response["error"])


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()