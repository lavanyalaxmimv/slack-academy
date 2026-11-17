from services import config
from services.discounts import add_request, get_request, set_status
from services.leave import is_manager

AUTO_APPROVE_LIMIT = 15.0
MAX_DISCOUNT = 40.0


def _input(block_id, action_id, label, placeholder="", multiline=False):
    element = {"type": "plain_text_input", "action_id": action_id, "multiline": multiline}
    if placeholder:
        element["placeholder"] = {"type": "plain_text", "text": placeholder}
    return {
        "type": "input",
        "block_id": block_id,
        "label": {"type": "plain_text", "text": label},
        "element": element,
    }


def discount_modal() -> dict:
    return {
        "type": "modal",
        "callback_id": "discount_modal",
        "title": {"type": "plain_text", "text": "Discount request"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            _input("account_block", "account", "Account", "e.g. Sharma Traders"),
            _input("value_block", "value", "Opportunity value (₹)", "e.g. 250000"),
            _input("discount_block", "discount", "Discount %", "e.g. 12.5"),
            _input("reason_block", "reason", "Justification", "Why does this deal need a discount?", True),
        ],
    }


def parse_number(text: str) -> float | None:
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return None


def approval_blocks(record: dict) -> list[dict]:
    rid = str(record["id"])
    return [
        {"type": "header", "text": {"type": "plain_text", "text": f"Discount request #{rid}"}},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Account*\n{record['account']}"},
                {"type": "mrkdwn", "text": f"*Requested by*\n<@{record['requester']}>"},
                {"type": "mrkdwn", "text": f"*Opportunity value*\n₹{record['value']:,.0f}"},
                {"type": "mrkdwn", "text": f"*Discount*\n{record['discount']:g}%"},
            ],
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Justification*\n{record['reason']}"}},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "action_id": "discount_approve",
                    "value": rid,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Reject"},
                    "style": "danger",
                    "action_id": "discount_reject",
                    "value": rid,
                },
            ],
        },
    ]


def open_modal(ack, command, client):
    ack()
    client.views_open(trigger_id=command["trigger_id"], view=discount_modal())


def handle_submission(ack, body, view, client):
    values = view["state"]["values"]
    account = (values["account_block"]["account"]["value"] or "").strip()
    value = parse_number(values["value_block"]["value"]["value"] or "")
    discount = parse_number(values["discount_block"]["discount"]["value"] or "")
    reason = (values["reason_block"]["reason"]["value"] or "").strip()

    errors = {}
    if not account:
        errors["account_block"] = "Please enter the account name."
    if value is None or value <= 0:
        errors["value_block"] = "Enter a positive number, for example 250000."
    if discount is None or discount < 0:
        errors["discount_block"] = "Enter a number, for example 12.5."
    elif discount > MAX_DISCOUNT:
        errors["discount_block"] = f"Discount cannot be more than {MAX_DISCOUNT:.0f}%."
    if len(reason) < 10:
        errors["reason_block"] = "Please give a reason (at least 10 characters)."

    if errors:
        ack(response_action="errors", errors=errors)
        return
    ack()

    requester = body["user"]["id"]
    needs_approval = discount > AUTO_APPROVE_LIMIT
    record = add_request(
        requester, account, value, discount, reason,
        "pending" if needs_approval else "approved",
    )

    if needs_approval:
        client.chat_postMessage(
            channel=config.APPROVALS_CHANNEL_ID,
            text=f"Discount request #{record['id']} from <@{requester}> needs approval",
            blocks=approval_blocks(record),
        )
        note = "was sent to the approvers."
    else:
        note = f"is within the {AUTO_APPROVE_LIMIT:g}% limit and was approved automatically."
    client.chat_postMessage(
        channel=requester,
        text=f"Your discount request #{record['id']} for {account} ({discount:g}%) {note}",
    )


def decide(ack, body, client, respond, action, approved):
    ack()
    approver = body["user"]["id"]
    if not is_manager(approver):
        respond(
            text="Sorry, only listed approvers can decide on discount requests.",
            replace_original=False,
            response_type="ephemeral",
        )
        return

    record = get_request(int(action["value"]))
    if record is None or record["status"] != "pending":
        return  # unknown request, or already decided

    verdict = "approved" if approved else "rejected"
    set_status(record["id"], verdict, approver)
    emoji = ":white_check_mark:" if approved else ":x:"
    blocks = [b for b in body["message"]["blocks"] if b["type"] != "actions"]
    blocks.append(
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"{emoji} *{verdict.capitalize()}* by <@{approver}>"}],
        }
    )
    client.chat_update(
        channel=body["channel"]["id"],
        ts=body["message"]["ts"],
        text=f"Discount request #{record['id']} {verdict}",
        blocks=blocks,
    )
    client.chat_postMessage(
        channel=record["requester"],
        text=f"Your discount request #{record['id']} for {record['account']} was {verdict} by <@{approver}>.",
    )


def approve(ack, body, client, respond, action):
    decide(ack, body, client, respond, action, True)


def reject(ack, body, client, respond, action):
    decide(ack, body, client, respond, action, False)


def register(app):
    app.command("/discount-lm")(open_modal)
    app.view("discount_modal")(handle_submission)
    app.action("discount_approve")(approve)
    app.action("discount_reject")(reject)