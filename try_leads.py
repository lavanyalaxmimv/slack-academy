from dotenv import load_dotenv

load_dotenv()

from services.leads import LeadError, create_lead


def attempt(label: str, **kwargs) -> None:
    try:
        lead_id = create_lead(**kwargs)
        print(f"{label}: OK, Lead ID = {lead_id}")
    except LeadError as error:
        print(f"{label}: FAILED with message -> {error}")


attempt("1. Valid lead", first_name="Priya", last_name="Nair", company="Sharma Traders", email="priya@example.com")
attempt("2. Missing last name", first_name="Priya", last_name="", company="Sharma Traders")
attempt("3. Bad email", first_name="Priya", last_name="Nair", company="Sharma Traders", email="not-an-email")