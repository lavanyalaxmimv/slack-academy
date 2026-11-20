from services.clients import create_salesforce_lead

result = create_salesforce_lead(
    first_name="Slack",
    last_name="Academy Test",
    company="CloudNova",
   
)

print("Lead creation successful:", result["success"])
print("Created Lead ID:", result["lead_id"])
