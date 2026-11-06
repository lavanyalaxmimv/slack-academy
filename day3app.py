import json
import logging
import os
import re
import sys
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

load_dotenv()


class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        data.update(getattr(record, "fields", {}))
        return json.dumps(data)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
log = logging.getLogger("academy")
log.setLevel(logging.INFO)
log.addHandler(handler)

app = App(token=os.environ["SLACK_BOT_TOKEN"])
NEW_HIRES_ID = os.environ["NEW_HIRES_CHANNEL_ID"]
ESCALATIONS_ID = os.environ["ESCALATIONS_CHANNEL_ID"]

CHECKLIST = (
    "Welcome to the team! Your onboarding checklist:\n"
    "1. Introduce yourself in #new-hires\n"
    "2. Read the pinned messages in #slack-training\n"
    "3. Set up your profile photo and time zone\n"
    "4. Ask your buddy any questions"
)

ORDERS = {
    "1001": "Packed, dispatching today",
    "1002": "In transit, due Monday",
    "1003": "Delivered on 4 Nov",
}

seen_events = set()


@app.event("member_joined_channel")
def welcome_new_member(event, client, context):
    if event["channel"] != NEW_HIRES_ID:
        return
    user_id = event["user"]
    if user_id == context.bot_user_id:
        return
    try:
        client.chat_postMessage(channel=user_id, text=CHECKLIST)
        log.info("welcome_dm_sent", extra={"fields": {"user": user_id}})
    except SlackApiError as e:
        log.error("welcome_dm_failed", extra={"fields": {"slack_error": e.response["error"]}})


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
    log.info("order_lookup", extra={"fields": {"order_id": order_id, "found": bool(status)}})


@app.message("trigger error")
def trigger_error(message):
    raise ValueError("Deliberate test error")


@app.event("message")
def ignore_other_messages():
    pass  # silences "unhandled event" warnings without logging message text


@app.event("reaction_added")
def escalate(event, body, client):
    if event["reaction"] != "rotating_light":
        return
    item = event["item"]
    if item["type"] != "message":
        return

    event_id = body["event_id"]
    if event_id in seen_events:
        log.info("duplicate_event_ignored", extra={"fields": {"event_id": event_id}})
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
        log.info("escalation_posted", extra={"fields": {"reporter": reporter, "author": author}})
    except SlackApiError as e:
        log.error("escalation_failed", extra={"fields": {"slack_error": e.response["error"]}})


@app.error
def global_error_handler(error, body):
    log.error(
        "unhandled_error",
        extra={
            "fields": {
                "error_type": type(error).__name__,
                "event_type": (body.get("event") or {}).get("type"),
            }
        },
    )


if __name__ == "__main__":
    log.info("app_starting")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()