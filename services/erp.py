import logging
import os
import time

import requests

log = logging.getLogger("academy.erp")

BASE_URL = os.environ.get("ERP_BASE_URL", "http://127.0.0.1:8000")
CLIENT_ID = os.environ.get("ERP_CLIENT_ID", "demo-id")


class ErpError(Exception):
    pass


class OrderNotFound(ErpError):
    pass


def get_order(order_id: str, max_attempts: int = 4, timeout: float = 3.0) -> dict:
    delay = 0.5
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                f"{BASE_URL}/orders/{order_id}",
                headers={"client_id": CLIENT_ID},
                timeout=timeout,
            )
            if response.status_code == 404:
                raise OrderNotFound(order_id)
            if response.status_code in (401, 403):
                raise ErpError("The ERP rejected our credentials.")
            if response.status_code >= 500:
                raise requests.HTTPError(f"status {response.status_code}")
            response.raise_for_status()
            return response.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
            log.warning("erp_retry attempt=%s/%s reason=%s", attempt, max_attempts, type(e).__name__)
            if attempt == max_attempts:
                raise ErpError("The ERP is not responding. Please try again later.") from e
            time.sleep(delay)
            delay *= 2  # back-off: 0.5s, 1s, 2s
    raise ErpError("Unexpected ERP failure.")