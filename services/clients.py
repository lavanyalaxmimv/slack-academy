
import os
import base64
import hashlib
import secrets
import requests

from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv(".env", override=True)


def generate_pkce_pair():
    verifier = secrets.token_urlsafe(64)

    digest = hashlib.sha256(verifier.encode("ascii")).digest()

    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    return verifier, challenge


def build_authorization_url(code_challenge):
    login_url = os.environ["SALESFORCE_LOGIN_URL"].rstrip("/")
    client_id = os.environ["SALESFORCE_CLIENT_ID"]
    callback_url = os.environ["SALESFORCE_CALLBACK_URL"]

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": callback_url,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    return f"{login_url}/services/oauth2/authorize?{urlencode(params)}"


def exchange_authorization_code(code, code_verifier):
    login_url = os.environ["SALESFORCE_LOGIN_URL"].rstrip("/")

    token_url = f"{login_url}/services/oauth2/token"

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.environ["SALESFORCE_CLIENT_ID"],
        "client_secret": os.environ["SALESFORCE_CLIENT_SECRET"],
        "redirect_uri": os.environ["SALESFORCE_CALLBACK_URL"],
        "code_verifier": code_verifier,
    }

    try:
        response = requests.post(
            token_url,
            data=payload,
            timeout=15,
        )
        response.raise_for_status()
        token_data = response.json()

    except requests.RequestException as exc:
        raise RuntimeError(
            "Salesforce token exchange failed. Check the connection and OAuth configuration."
        ) from exc

    except ValueError as exc:
        raise RuntimeError(
            "Salesforce returned an invalid token response."
        ) from exc

    if not token_data.get("access_token") or not token_data.get("instance_url"):
        raise RuntimeError(
            f"Salesforce did not return the required authentication details: "
            f"{token_data.get('error', 'Unknown OAuth error')}"
        )

    return token_data


def verify_salesforce_connection():
    instance_url = os.environ["SALESFORCE_INSTANCE_URL"]
    access_token = os.environ["SALESFORCE_ACCESS_TOKEN"]

    response = requests.get(
        f"{instance_url}/services/data/",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        timeout=15,
    )

    response.raise_for_status()

    versions = response.json()

    return {
        "connected": True,
        "available_api_versions": len(versions),
        "latest_api_version": versions[-1]["version"],
    }

def create_salesforce_lead(first_name, last_name, company, email=None):
    instance_url = os.environ["SALESFORCE_INSTANCE_URL"]
    access_token = os.environ["SALESFORCE_ACCESS_TOKEN"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    lead_data = {
        "LastName": last_name,
        "Company": company,
    }

    if first_name:
        lead_data["FirstName"] = first_name

    if email:
        lead_data["Email"] = email

    try:
        response = requests.post(
            f"{instance_url}/services/data/v68.0/sobjects/Lead/",
            headers=headers,
            json=lead_data,
            timeout=15,
        )

        response.raise_for_status()
        result = response.json()

        return {
            "success": result.get("success", False),
            "lead_id": result.get("id"),
        }

    
    
    except requests.RequestException as exc:
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else "No HTTP response"
        )

        error_details = (
            exc.response.text
            if exc.response is not None
            else str(exc)
        )

        raise RuntimeError(
            f"Salesforce Lead creation failed. "
            f"Status: {status_code}. "
            f"Details: {error_details}"
        ) from exc
