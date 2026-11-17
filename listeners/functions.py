from services.leads import LeadError, create_lead


def create_lead_step(inputs, complete, fail, logger):
    try:
        lead_id = create_lead(
            first_name=str(inputs.get("first_name", "")),
            last_name=str(inputs.get("last_name", "")),
            company=str(inputs.get("company", "")),
            email=str(inputs.get("email", "")),
        )
    except LeadError as error:
        logger.warning("create_lead_failed")
        fail(str(error))
        return

    complete(outputs={"lead_id": lead_id})