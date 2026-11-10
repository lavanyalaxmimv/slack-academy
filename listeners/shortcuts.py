from slack_sdk.errors import SlackApiError

from services.tasks import add_task


def create_task(ack, shortcut, client):
    ack()
    message = shortcut["message"]
    channel_id = shortcut["channel"]["id"]
    user_id = shortcut["user"]["id"]

    try:
        permalink = client.chat_getPermalink(
            channel=channel_id, message_ts=message["ts"]
        )["permalink"]
    except SlackApiError as e:
        print("Could not get permalink:", e.response["error"])
        permalink = ""

    task = add_task(
        text=message.get("text", ""),
        author=message.get("user", "unknown"),
        created_by=user_id,
        permalink=permalink,
    )
    print(f"Task {task['id']} saved")

    try:
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=f"Task #{task['id']} created from that message.",
        )
    except SlackApiError:
        pass  # the confirmation is optional if the bot is not in the channel


def register(app):
    app.shortcut("create_task")(create_task)