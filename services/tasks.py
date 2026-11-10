import json
from datetime import UTC, datetime

TASKS_FILE = "tasks.json"


def load_tasks() -> list[dict]:
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("tasks.json is not valid JSON, starting a new list")
        return []


def save_tasks(tasks: list[dict]) -> None:
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def add_task(text: str, author: str, created_by: str, permalink: str) -> dict:
    tasks = load_tasks()
    task = {
        "id": len(tasks) + 1,
        "text": text,
        "author": author,
        "created_by": created_by,
        "permalink": permalink,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    tasks.append(task)
    save_tasks(tasks)
    return task