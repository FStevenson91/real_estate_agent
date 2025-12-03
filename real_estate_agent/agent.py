from google.adk.agents import Agent
from google.genai import types
from .prompt import agent_prompt
from .tools import detect_location


real_estate_agent = Agent(
    name="real_state_agent",
    model="gemini-2.0-flash",
    description="real estate agent that qualifies leads using the BANT criteria in a few steps.",
    instruction=agent_prompt,
     tools =[detect_location]
    #  generate_content_config=types.GenerateContentConfig(temperature=0.5)
)