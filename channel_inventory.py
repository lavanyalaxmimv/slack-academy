import csv
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def list_public_channels(page_size=10):
    channels = []
    pages = 0
    for page in client.conversations_list(
        types="public_channel",
        exclude_archived=True,
        limit=page_size,
    ):
        pages += 1
        for ch in page["channels"]:
            channels.append(
                {
                    "name": ch["name"],
                    "members": ch.get("num_members", 0),
                    "purpose": ch["purpose"]["value"],
                }
            )
    print(f"Fetched {len(channels)} channels across {pages} pages")
    return channels


def save_csv(rows, path="channels.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "members", "purpose"])
        writer.writeheader()
        writer.writerows(rows)
    print("Saved", path)


if __name__ == "__main__":
    try:
        rows = list_public_channels()
        for row in rows:
            print(f"#{row['name']} | {row['members']} members | {row['purpose']}")
        save_csv(rows)
    except SlackApiError as e:
        print("Slack error:", e.response["error"])