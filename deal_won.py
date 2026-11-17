import os

import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.environ.get("DEAL_WEBHOOK_URL")

DEAL = {
    "account": "Sharma Traders",
    "amount": 2450000,
    "owner": "Priya Nair",
    "stage": "Closed Won",
    "close_date": "2026-11-12",
    "url": "https://example.my.salesforce.com/lightning/r/Opportunity/006XXXXXXXXXXXX/view",
}


def build_card(deal: dict) -> dict:
    return {
        "text": f"Deal won: {deal['account']} (₹{deal['amount']:,.0f})",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": ":tada: Deal won", "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Account*\n{deal['account']}"},
                    {"type": "mrkdwn", "text": f"*Amount*\n₹{deal['amount']:,.0f}"},
                    {"type": "mrkdwn", "text": f"*Owner*\n{deal['owner']}"},
                    {"type": "mrkdwn", "text": f"*Close date*\n{deal['close_date']}"},
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Open in Salesforce"},
                        "url": deal["url"],
                    }
                ],
            },
        ],
    }


def post_card(card: dict) -> bool:
    if not WEBHOOK_URL:
        print("DEAL_WEBHOOK_URL is not set in .env")
        return False
    try:
        response = requests.post(WEBHOOK_URL, json=card, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        # Print only the error type: the message can contain the secret URL.
        print("Webhook call failed:", type(e).__name__)
        return False
    print("Deal card posted")
    return True


if __name__ == "__main__":
    post_card(build_card(DEAL))