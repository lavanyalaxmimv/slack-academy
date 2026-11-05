import os
import time
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
CHANNEL_ID = os.environ["DIGEST_CHANNEL_ID"]


def count_messages_last_24h(channel_id):
    oldest = time.time() - 24 * 60 * 60
    counts = {}
    for page in client.conversations_history(
        channel=channel_id, oldest=str(oldest), limit=100
    ):
        for msg in page["messages"]:
            if msg.get("bot_id") or msg.get("subtype"):
                continue  # skip bots and system messages
            user = msg.get("user")
            if user:
                counts[user] = counts.get(user, 0) + 1
    return counts


def user_name(user_id, cache):
    if user_id not in cache:
        info = client.users_info(user=user_id)
        cache[user_id] = info["user"].get("real_name") or info["user"]["name"]
    return cache[user_id]


def build_summary(counts):
    if not counts:
        return "No messages in the last 24 hours."
    cache = {}
    lines = []
    for user_id, n in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"• {user_name(user_id, cache)}: {n}")
    return "\n".join(lines)


if __name__ == "__main__":
    try:
        try:
            client.conversations_join(channel=CHANNEL_ID)
        except SlackApiError:
            pass  # already a member, or not a public channel

        counts = count_messages_last_24h(CHANNEL_ID)
        summary = build_summary(counts)
        print(summary)

        parent = client.chat_postMessage(
            channel=CHANNEL_ID, text="Channel digest: last 24 hours"
        )
        client.chat_postMessage(
            channel=CHANNEL_ID, thread_ts=parent["ts"], text=summary
        )
        print("Digest posted as a thread reply.")
    except SlackApiError as e:
        print("Slack error:", e.response["error"])