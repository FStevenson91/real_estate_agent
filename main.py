from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from dotenv import load_dotenv
from real_estate_agent.agent import real_estate_agent
import asyncio
import json

load_dotenv(override=True)

APP_NAME="real_estate_agent"

# Simulates WhatsApp number (in production comes from the webhook)
PHONE_NUMBER= input("Phone number (simulated): ")
# Phone = user_id = i
USER_ID=PHONE_NUMBER
SESSION_ID=PHONE_NUMBER # same number to keep context

session_service = InMemorySessionService()

asyncio.run(session_service.create_session(
    app_name=APP_NAME, 
    user_id=USER_ID, 
    session_id=SESSION_ID,
    state={"user_id": PHONE_NUMBER} # Save in state for the callback
    ))

runner = Runner(
    agent=real_estate_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

while True:
    user_msg = input("You: ")
    if user_msg == "exit": 
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
            response_text = event.content.parts[0].text
            
            clean_text = response_text.replace("```json", "").replace("```", "").strip()

            # Parse JSON
            try:
                response_data = json.loads(clean_text)
                message = response_data.get("message", response_text)
                should_escalate = response_data.get("should_escalate", False)
                
                print("Agent: " + message)
                
                if should_escalate:
                    print("⚠️ ESCALANDO A HUMANO...")
                    
            except json.JSONDecodeError:
                # If it is not valid JSON, display it as-is
                print("Agent: " + response_text)