from services import config
from services.leave import request_blocks
from services.orders import OrderRepository, order_blocks

repo = OrderRepository()


def order_status(ack, command, respond):
    print("order_status called with:", command["text"])
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


def leave_request(ack, command, client, respond):
    ack()
    details = command["text"].strip()
    if not details:
        respond("Please add your dates and reason, for example: /leave-request 12-13 Nov, family function")
        return
    requester = command["user_id"]
    client.chat_postMessage(
        channel=config.NEW_MANAGERS_CHANNEL_ID,
        text=f"Leave request from <@{requester}>: {details}",
        blocks=request_blocks(requester, details),
    )
    respond("Your leave request has been sent to the managers.")


def register(app):
    app.command("/order-status-lm")(order_status)
    app.command("/leave-request")(leave_request)