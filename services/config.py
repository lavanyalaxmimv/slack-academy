import os

from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
NEW_MANAGERS_CHANNEL_ID = os.environ["NEW_MANAGERS_CHANNEL_ID"]
MANAGER_IDS = {m.strip() for m in os.environ["MANAGER_IDS"].split(",") if m.strip()}
APPROVALS_CHANNEL_ID = os.environ["APPROVALS_CHANNEL_ID"]