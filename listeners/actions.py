from services.leave import is_manager


def decide(ack, body, client, respond, action, approved):
    ack()
    manager = body["user"]["id"]
    requester = action["value"]

    if not is_manager(manager):
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


def approve(ack, body, client, respond, action):
    decide(ack, body, client, respond, action, True)


def reject(ack, body, client, respond, action):
    decide(ack, body, client, respond, action, False)


def register(app):
    app.action("leave_approve")(approve)
    app.action("leave_reject")(reject)