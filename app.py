
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def join_test_channel():
    channel_id = os.environ.get("TEST_CHANNEL_ID")
    if not channel_id:
        return
    try:
        app.client.conversations_join(channel=channel_id)
        print("Bot joined the test channel.")
    except SlackApiError as e:
        print("Join skipped:", e.response["error"])


@app.event("app_mention")
def handle_mention(event, client, say):
    
    user_id = event["user"]
    info = client.users_info(user=user_id)
    name = info["user"].get("real_name") or info["user"]["name"]
    thread_ts = event.get("thread_ts") or event["ts"]
    say(text=f"Hi {name}! Academy Bot is listening.", thread_ts=thread_ts)


if __name__ == "__main__":
    join_test_channel()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()