from dataclasses import dataclass


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