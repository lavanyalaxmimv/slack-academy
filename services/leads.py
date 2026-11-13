import json
import os
import uuid
from datetime import datetime, timezone

MOCK_FILE = os.path.join("data", "mock_leads.json")


class LeadError(Exception):
    """An error whose message is safe to show to workflow users."""


def validate(last_name: str, company: str, email: str) -> None:
    if not last_name.strip():
        raise LeadError("Last name is required to create a lead.")
    if not company.strip():
        raise LeadError("Company is required to create a lead.")
    if email and "@" not in email:
        raise LeadError("That email address does not look valid.")


def _load_mock() -> list[dict]:
    try:
        with open(MOCK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _create_mock(fields: dict) -> str:
    leads = _load_mock()
    lead_id = "00Q" + uuid.uuid4().hex[:15].upper()
    leads.append(
        {
            "Id": lead_id,
            **fields,
            "CreatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )
    os.makedirs("data", exist_ok=True)
    with open(MOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    return lead_id


def _create_salesforce(fields: dict) -> str:
    from simple_salesforce import Salesforce
    from simple_salesforce.exceptions import SalesforceError

    try:
        sf = Salesforce(
            instance_url=os.environ["SF_INSTANCE_URL"],
            session_id=os.environ["SF_ACCESS_TOKEN"],
        )
        result = sf.Lead.create(fields)
    except KeyError as exc:
        raise LeadError("The Salesforce settings are missing from .env.") from exc
    except SalesforceError as exc:
        status = getattr(exc, "status", "unknown")
        raise LeadError(f"Salesforce rejected the lead (status {status}).") from exc
    except Exception as exc:
        raise LeadError("Could not reach Salesforce.") from exc
    return result["id"]


def create_lead(first_name: str, last_name: str, company: str, email: str = "") -> str:
    validate(last_name, company, email)
    fields = {
        "FirstName": first_name.strip(),
        "LastName": last_name.strip(),
        "Company": company.strip(),
        "Email": email.strip(),
    }
    if os.environ.get("LEADS_BACKEND", "mock") == "salesforce":
        return _create_salesforce(fields)
    return _create_mock(fields)