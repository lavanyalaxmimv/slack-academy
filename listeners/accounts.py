import logging

import requests
from simple_salesforce.exceptions import SalesforceError

from services.accounts import search_accounts

log = logging.getLogger("academy.accounts")


def account_blocks(a: dict) -> list[dict]:
    if a["opps"]:
        lines = "\n".join(
            f"• {o['name']}: ₹{o['amount']:,.0f} ({o['stage']})" for o in a["opps"]
        )
    else:
        lines = "No open opportunities."
    return [
        {"type": "header", "text": {"type": "plain_text", "text": a["name"]}},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Owner*\n{a['owner']}"},
                {"type": "mrkdwn", "text": f"*Last activity*\n{a['last_activity'] or 'None recorded'}"},
            ],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Open opportunities ({len(a['opps'])})*\n{lines}"},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Open in Salesforce"},
                    "url": a["url"],
                }
            ],
        },
    ]


def account_command(ack, command, respond):
    ack()
    name = command["text"].strip()
    if len(name) < 2:
        respond("Please type at least two letters of the account name, for example: /account-lm Sharma")
        return
    try:
        matches = search_accounts(name)
    except (requests.RequestException, SalesforceError) as e:
        log.error("account_lookup_failed: %s", type(e).__name__)
        respond("Could not reach Salesforce right now. Please try again shortly.")
        return

    if not matches:
        respond(f"No account found matching \"{name}\".")
    elif len(matches) > 1:
        names = "\n".join(f"• {m['name']}" for m in matches)
        respond(f"Found {len(matches)} accounts. Please be more specific:\n{names}")
    else:
        respond(blocks=account_blocks(matches[0]), text=f"Account: {matches[0]['name']}")


def register(app):
    app.command("/account-lm")(account_command)