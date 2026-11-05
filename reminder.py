import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
CHANNEL_ID = os.environ["DIGEST_CHANNEL_ID"]
IST = timezone(timedelta(hours=5, minutes=30))


def tomorrow_930_ist():
    tomorrow = datetime.now(IST) + timedelta(days=1)
    return tomorrow.replace(hour=9, minute=30, second=0, microsecond=0)


def schedule_reminder():
    when = tomorrow_930_ist()
    response = client.chat_scheduleMessage(
        channel=CHANNEL_ID,
        post_at=int(when.timestamp()),
        text="Stand-up in 5 minutes. Please post your update in the thread.",
    )
    print("Scheduled for", when.strftime("%a %d %b %Y %H:%M IST"))
    return response["scheduled_message_id"]


def list_scheduled():
    result = client.chat_scheduledMessages_list(channel=CHANNEL_ID)
    items = result["scheduled_messages"]
    print(f"{len(items)} scheduled message(s):")
    for item in items:
        when = datetime.fromtimestamp(item["post_at"], IST)
        print(" ", item["id"], when.strftime("%d %b %H:%M IST"))
    return items


def delete_scheduled(message_id):
    client.chat_deleteScheduledMessage(
        channel=CHANNEL_ID, scheduled_message_id=message_id
    )
    print("Deleted", message_id)


if __name__ == "__main__":
    try:
        message_id = schedule_reminder()
        list_scheduled()
        delete_scheduled(message_id)
        list_scheduled()
    except SlackApiError as e:
        print("Slack error:", e.response["error"])