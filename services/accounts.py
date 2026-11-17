import os

import requests
from simple_salesforce import Salesforce, format_soql

MOCK_ACCOUNTS = [
    {
        "id": "001MOCK0001", "name": "Sharma Traders", "owner": "Priya Nair",
        "last_activity": "2026-11-09",
        "opps": [
            {"name": "Q4 rice supply", "amount": 2450000, "stage": "Negotiation"},
            {"name": "Oil renewal", "amount": 480000, "stage": "Proposal"},
        ],
    },
    {
        "id": "001MOCK0002", "name": "Sharma Textiles", "owner": "Arun Das",
        "last_activity": "2026-10-28", "opps": [],
    },
    {
        "id": "001MOCK0003", "name": "Gupta Stores", "owner": "Priya Nair",
        "last_activity": None,
        "opps": [{"name": "Tea restock", "amount": 150000, "stage": "Prospecting"}],
    },
]

MOCK_BASE = "https://example.my.salesforce.com"


def _mock_search(name: str) -> list[dict]:
    needle = name.lower()
    return [
        {**a, "url": f"{MOCK_BASE}/lightning/r/Account/{a['id']}/view"}
        for a in MOCK_ACCOUNTS
        if needle in a["name"].lower()
    ]


def _salesforce_client() -> tuple[Salesforce, str]:
    domain = os.environ["SF_DOMAIN_URL"].rstrip("/")
    response = requests.post(
        f"{domain}/services/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["SF_CLIENT_ID"],
            "client_secret": os.environ["SF_CLIENT_SECRET"],
        },
        timeout=10,
    )
    response.raise_for_status()
    token = response.json()
    sf = Salesforce(instance_url=token["instance_url"], session_id=token["access_token"])
    return sf, token["instance_url"]


def _salesforce_search(name: str) -> list[dict]:
    sf, instance_url = _salesforce_client()
    query = format_soql(
        "SELECT Id, Name, Owner.Name, LastActivityDate, "
        "(SELECT Name, Amount, StageName FROM Opportunities WHERE IsClosed = false "
        "ORDER BY Amount DESC LIMIT 5) "
        "FROM Account WHERE Name LIKE '%{:like}%' LIMIT 5",
        name,
    )
    accounts = []
    for r in sf.query(query)["records"]:
        opps = (r.get("Opportunities") or {}).get("records", [])
        accounts.append(
            {
                "id": r["Id"],
                "name": r["Name"],
                "owner": (r.get("Owner") or {}).get("Name", "Unknown"),
                "last_activity": r.get("LastActivityDate"),
                "opps": [
                    {"name": o["Name"], "amount": o.get("Amount") or 0, "stage": o["StageName"]}
                    for o in opps
                ],
                "url": f"{instance_url}/lightning/r/Account/{r['Id']}/view",
            }
        )
    return accounts


def using_salesforce() -> bool:
    return all(os.environ.get(k) for k in ("SF_DOMAIN_URL", "SF_CLIENT_ID", "SF_CLIENT_SECRET"))


def search_accounts(name: str) -> list[dict]:
    return _salesforce_search(name) if using_salesforce() else _mock_search(name)