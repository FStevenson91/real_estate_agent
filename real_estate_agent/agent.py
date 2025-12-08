from google.adk.agents import Agent
from google.genai import types
from .prompt import agent_prompt
from .tools import detect_location, create_contact, get_contact, update_contact, list_contacts
from .callbacks import before_model_callback


real_estate_agent = Agent(
    name="real_state_agent",
    model="gemini-2.0-flash",
    description="real estate agent that qualifies leads using the BANT criteria in a few steps.",
    instruction=agent_prompt,
    tools =[detect_location, create_contact, get_contact, update_contact, list_contacts],
    before_model_callback=before_model_callback
    #  generate_content_config=types.GenerateContentConfig(temperature=0.5)
)