import re
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

ORDERS = {
    "1001": "Packed, dispatching today",
    "1002": "In transit, due Monday",
    "1003": "Delivered on 4 Nov",
}

@app.message(re.compile(r"order #(\d+)", re.IGNORECASE))
def order_status(message, context, say):
    if message.get("bot_id"):
        return
    order_id = context["matches"][0]
    status = ORDERS.get(order_id)
    thread_ts = message.get("thread_ts") or message["ts"]
    if status:
        say(text=f"Order #{order_id}: {status}", thread_ts=thread_ts)
    else:
        say(
            text=f"Sorry, I couldn't find order #{order_id}. Please check the number and try again.",
            thread_ts=thread_ts,
        )
        
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()