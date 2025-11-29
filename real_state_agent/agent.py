from google.adk.agents import Agent
from google.genai import types
from .prompt import agent_prompt


real_state_agent = Agent(
    name="real_state_agent",
    model="gemini-2.0-flash",
    description="agente inmobiliario que califica criterios BANT en pocos pasos",
    instruction=agent_prompt,
    #  generate_content_config=types.GenerateContentConfig(temperature=0.5)
)