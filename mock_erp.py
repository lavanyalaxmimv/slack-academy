from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

ORDERS = {
    "1001": {"order_id": "1001", "status": "Packed, dispatching today", "credit_ok": True},
    "1002": {"order_id": "1002", "status": "In transit, due Monday", "credit_ok": True},
    "1003": {"order_id": "1003", "status": "On credit hold", "credit_ok": False},
}
attempts: dict[str, int] = {}


@app.get("/orders/{order_id}")
def get_order(
    order_id: str,
    client_id: str | None = Header(default=None, convert_underscores=False),
):
    if client_id != "demo-id":
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="Order not found")
    attempts[order_id] = attempts.get(order_id, 0) + 1
    if attempts[order_id] <= 2:
        raise HTTPException(status_code=503, detail="Temporary ERP error")
    return ORDERS[order_id]