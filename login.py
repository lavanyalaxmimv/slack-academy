
from dotenv import set_key

from services.clients import (
    build_authorization_url,
    exchange_authorization_code,
)
from services.callback import get_authorization_code


def main():
    print("\nOpen this Salesforce authorization URL in your browser:\n")
    print(build_authorization_url())

    # Wait for Salesforce to redirect to localhost.
    code = get_authorization_code()

    print("\nAuthorization code received.")

    # Exchange the code for Salesforce tokens.
    token_data = exchange_authorization_code(code)

    # Store tokens locally in .env. Never print their values.
    set_key(".env", "SALESFORCE_ACCESS_TOKEN", token_data["access_token"])
    set_key(".env", "SALESFORCE_INSTANCE_URL", token_data["instance_url"])

    if token_data.get("refresh_token"):
        set_key(".env", "SALESFORCE_REFRESH_TOKEN", token_data["refresh_token"])

    print("\nSalesforce OAuth authentication successful!")
    print("Instance URL and access token saved locally.")


if __name__ == "__main__":
    main()
