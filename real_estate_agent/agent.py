from google.adk.agents import Agent
from google.genai import types
from .tools import create_contact, get_contact, update_contact, list_contacts
from .callbacks import before_model_callback
from pydantic import BaseModel

class AgentResponse(BaseModel):
    message: str        
    should_escalate: bool

real_estate_agent = Agent(
    name="real_estate_agent",
    model="gemini-2.0-flash",
    description="real estate agent that qualifies leads using the BANT criteria in a few steps.",
    instruction="",
    tools =[create_contact, get_contact, update_contact, list_contacts],
    before_model_callback=before_model_callback,
    output_schema=AgentResponse,
    generate_content_config=types.GenerateContentConfig(temperature=0.7)
)