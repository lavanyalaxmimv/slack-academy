from datetime import datetime, timedelta, timezone

from services.discounts import all_requests
from services.leave import is_manager

IST = timezone(timedelta(hours=5, minutes=30))


def request_lines(items: list[dict]) -> str:
    return "\n".join(
        f"• #{r['id']} *{r['account']}*, {r['discount']:g}% on ₹{r['value']:,.0f} "
        f"from <@{r['requester']}>"
        for r in items[:10]
    )


def list_section(title: str, items: list[dict], empty_text: str) -> list[dict]:
    if not items:
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*"}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": empty_text}]},
        ]
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{title}* ({len(items)})\n{request_lines(items)}"},
        }
    ]


def build_home(user_id: str) -> dict:
    requests = all_requests()
    total = len(requests)
    pending = sum(1 for r in requests if r["status"] == "pending")
    approved = sum(1 for r in requests if r["status"] == "approved")
    rejected = sum(1 for r in requests if r["status"] == "rejected")
    average = sum(r["discount"] for r in requests) / total if total else 0.0

    mine_pending = [r for r in requests if r["requester"] == user_id and r["status"] == "pending"]
    manager = is_manager(user_id)
    waiting = [r for r in requests if r["status"] == "pending"] if manager else []
    refreshed = datetime.now(IST).strftime("%H:%M:%S IST")

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "Discount approvals"}},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Total requests*\n{total}"},
                {"type": "mrkdwn", "text": f"*Pending*\n{pending}"},
                {"type": "mrkdwn", "text": f"*Approved*\n{approved}"},
                {"type": "mrkdwn", "text": f"*Rejected*\n{rejected}"},
                {"type": "mrkdwn", "text": f"*Average discount*\n{average:.1f}%"},
            ],
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Refresh"},
                    "action_id": "home_refresh",
                }
            ],
        },
        {"type": "context", "elements": [{"type": "mrkdwn", "text": f"Last refreshed {refreshed}"}]},
        {"type": "divider"},
    ]
    blocks += list_section("Your pending requests", mine_pending, "You have no pending requests.")
    if manager:
        blocks += list_section("Awaiting your approval", waiting, "Nothing is waiting for your approval.")
    return {"type": "home", "blocks": blocks}


def publish_home(client, user_id: str) -> None:
    client.views_publish(user_id=user_id, view=build_home(user_id))


def app_home_opened(event, client):
    if event.get("tab") != "home":
        return
    publish_home(client, event["user"])


def refresh(ack, body, client):
    ack()
    publish_home(client, body["user"]["id"])


def register(app):
    app.event("app_home_opened")(app_home_opened)
    app.action("home_refresh")(refresh)