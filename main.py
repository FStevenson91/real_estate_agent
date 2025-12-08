from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from dotenv import load_dotenv
from real_estate_agent.agent import real_estate_agent
import asyncio

load_dotenv(override=True)

APP_NAME="real_estate_agent"
USER_ID="user_1"
SESSION_ID="session_1"

session_service = InMemorySessionService()

asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID))

runner = Runner(
    agent=real_estate_agent,
    app_name=APP_NAME,
    session_service=session_service
)

while True:
    user_msg = input("Tu: ")
    if user_msg == "salir": 
        break
    content = Content(
        role="user", 
        parts=[Part(text=user_msg)])

    events = runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    )

    for event in events:
        if event.is_final_response() and event.content:
           response = event.content.parts[0].text
           print("Agente: " + response)