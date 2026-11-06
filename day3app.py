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
ESCALATIONS_ID = os.environ["ESCALATIONS_CHANNEL_ID"]
seen_events = set()


@app.event("reaction_added")
def escalate(event, body, client):
    if event["reaction"] != "rotating_light":
        return
    item = event["item"]
    if item["type"] != "message":
        return

    event_id = body["event_id"]
    if event_id in seen_events:
        print("Duplicate event ignored")
        return
    seen_events.add(event_id)

    channel = item["channel"]
    ts = item["ts"]
    reporter = event["user"]
    try:
        permalink = client.chat_getPermalink(channel=channel, message_ts=ts)["permalink"]
        history = client.conversations_history(
            channel=channel, latest=ts, inclusive=True, limit=1
        )
        author = history["messages"][0].get("user", "unknown")
        client.chat_postMessage(
            channel=ESCALATIONS_ID,
            text=(
                f":rotating_light: Escalation raised by <@{reporter}> "
                f"on a message from <@{author}>\n{permalink}"
            ),
        )
        print("Escalation posted")
    except SlackApiError as e:
        print("Escalation failed:", e.response["error"])
        
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()