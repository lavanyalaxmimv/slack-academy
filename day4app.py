import os
from dataclasses import dataclass
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@dataclass
class Order:
    order_id: str
    customer: str
    status: str
    amount: float


class OrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {
            "1001": Order("1001", "Sharma Traders", "Packed, dispatching today", 45200.0),
            "1002": Order("1002", "Gupta Stores", "In transit, due Monday", 18750.5),
            "1003": Order("1003", "Mehta Wholesale", "Delivered on 4 Nov", 92300.0),
        }

    def get(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)


repo = OrderRepository()


def order_blocks(order: Order) -> list[dict]:
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Order #{order.order_id}*"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Customer*\n{order.customer}"},
                {"type": "mrkdwn", "text": f"*Status*\n{order.status}"},
                {"type": "mrkdwn", "text": f"*Amount*\n₹{order.amount:,.2f}"},
            ],
        },
    ]


@app.command("/order-status")
def order_status(ack, command, respond):
    ack()
    order_id = command["text"].strip().lstrip("#")
    if not order_id:
        respond("Please give an order ID, for example: /order-status 1001")
        return
    order = repo.get(order_id)
    if order is None:
        respond(f"Sorry, I couldn't find order #{order_id}. Please check the number and try again.")
        return
    respond(blocks=order_blocks(order), text=f"Order #{order.order_id}: {order.status}")
NEW_MANAGERS_CHANNEL_ID = os.environ["NEW_MANAGERS_CHANNEL_ID"]
MANAGER_IDS = {m.strip() for m in os.environ["MANAGER_IDS"].split(",") if m.strip()}


def request_blocks(requester: str, details: str) -> list[dict]:
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Leave request* from <@{requester}>\n{details}"},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "action_id": "leave_approve",
                    "value": requester,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Reject"},
                    "style": "danger",
                    "action_id": "leave_reject",
                    "value": requester,
                },
            ],
        },
    ]


@app.command("/leave-request")
def leave_request(ack, command, client, respond):
    ack()
    details = command["text"].strip()
    if not details:
        respond("Please add your dates and reason, for example: /leave-request 12-13 Nov, family function")
        return
    requester = command["user_id"]
    client.chat_postMessage(
        channel=NEW_MANAGERS_CHANNEL_ID,
        text=f"Leave request from <@{requester}>: {details}",
        blocks=request_blocks(requester, details),
    )
    respond("Your leave request has been sent to the managers.")


def decide(ack, body, client, respond, action, approved: bool):
    ack()
    manager = body["user"]["id"]
    requester = action["value"]

    if manager not in MANAGER_IDS:
        respond(
            text="Sorry, only listed managers can approve or reject leave requests.",
            replace_original=False,
            response_type="ephemeral",
        )
        return

    blocks = body["message"]["blocks"]
    if not any(b["type"] == "actions" for b in blocks):
        return  # already decided by another manager

    verdict = "Approved" if approved else "Rejected"
    emoji = ":white_check_mark:" if approved else ":x:"
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"Leave request {verdict.lower()}",
        blocks=[
            blocks[0],
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"{emoji} *{verdict}* by <@{manager}>"}],
            },
        ],
    )
    client.chat_postMessage(
        channel=requester,
        text=f"Your leave request was {verdict.lower()} by <@{manager}>.",
    )


@app.action("leave_approve")
def approve(ack, body, client, respond, action):
    decide(ack, body, client, respond, action, True)


@app.action("leave_reject")
def reject(ack, body, client, respond, action):
    decide(ack, body, client, respond, action, False)

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()