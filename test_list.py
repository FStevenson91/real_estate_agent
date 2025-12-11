from dotenv import load_dotenv
load_dotenv(override=True)

from real_estate_agent.tools.crm import list_contacts

result = list_contacts(search_term="felipe")
print(result)