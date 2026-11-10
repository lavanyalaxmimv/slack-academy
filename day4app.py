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


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()