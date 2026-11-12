import json
import os
from datetime import datetime, timezone

STORE_FILE = os.path.join("data", "discounts.json")


def _load() -> list[dict]:
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(items: list[dict]) -> None:
    os.makedirs("data", exist_ok=True)
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


def all_requests() -> list[dict]:
    return _load()


def add_request(
    requester: str, account: str, value: float, discount: float, reason: str, status: str
) -> dict:
    items = _load()
    record = {
        "id": len(items) + 1,
        "requester": requester,
        "account": account,
        "value": value,
        "discount": discount,
        "reason": reason,
        "status": status,
        "decided_by": None,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    items.append(record)
    _save(items)
    return record


def get_request(request_id: int) -> dict | None:
    return next((r for r in _load() if r["id"] == request_id), None)


def set_status(request_id: int, status: str, decided_by: str) -> dict | None:
    items = _load()
    for record in items:
        if record["id"] == request_id:
            record["status"] = status
            record["decided_by"] = decided_by
            _save(items)
            return record
    return None