import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
CHANNEL_ID = os.environ["DIGEST_CHANNEL_ID"]


def upload_report(path="channels.csv"):
    if not os.path.exists(path):
        print(f"{path} not found. Run channel_inventory.py first.")
        return
    response = client.files_upload_v2(
        channel=CHANNEL_ID,
        file=path,
        title="Channel inventory",
        initial_comment="Channel inventory report (Lab 2.4)",
    )
    file_info = response.get("file") or {}
    print("Uploaded file id:", file_info.get("id"))


if __name__ == "__main__":
    try:
        upload_report()
    except SlackApiError as e:
        print("Slack error:", e.response["error"])