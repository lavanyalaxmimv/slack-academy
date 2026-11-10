from services import config


def is_manager(user_id: str) -> bool:
    return user_id in config.MANAGER_IDS


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