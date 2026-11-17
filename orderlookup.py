import logging

from services.erp import ErpError, OrderNotFound, get_order

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

for order_id in ("1001", "9999"):
    try:
        order = get_order(order_id)
        print(f"Order {order_id}: {order['status']}")
    except OrderNotFound:
        print(f"Order {order_id}: not found")
    except ErpError as e:
        print(f"Order {order_id}: {e}")