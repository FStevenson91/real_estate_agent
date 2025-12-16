# Service to run the agent and process responses

import json
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from real_estate_agent.agent import root_agent
from models.payloads import AgentResponse

APP_NAME = "real_estate_agent"

# Services (in production this uses real persistence)
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def get_or_create_session(phone_number: str):
    """
    Gets or creates a session for the phone number.
    Maintains the conversation context.
    """
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=phone_number,
            session_id=phone_number
        )
        if not session:
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=phone_number,
                session_id=phone_number,
                state={"user_id": phone_number}
            )
        return session
    except Exception:
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=phone_number,
            session_id=phone_number,
            state={"user_id": phone_number}
        )
        return session


def parse_agent_response(response_text: str) -> AgentResponse:
    """
    Parses the agent's JSON response.
    Cleans markdown backticks if they exist.
    """
    clean_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(clean_text)
        return AgentResponse(
            message=data.get("message", response_text),
            should_escalate=data.get("should_escalate", False)
        )
    except json.JSONDecodeError:
        return AgentResponse(
            message=response_text,
            should_escalate=False
        )


async def process_message(phone_number: str, message_text: str) -> AgentResponse:
    """
    Processes a user message with the agent.

    Args:
        phone_number: User's phone number
        message_text: Message text

    Returns:
        AgentResponse with message and should_escalate
    """
    # Get or create session
    await get_or_create_session(phone_number)
    
    # Prepare message for the agent
    content = Content(
        role="user",
        parts=[Part(text=message_text)]
    )
    
    # Run the agent
    events = runner.run(
        user_id=phone_number,
        session_id=phone_number,
        new_message=content
    )
    
    # Get final response
    for event in events:
        if event.is_final_response() and event.content:
            response_text = event.content.parts[0].text
            return parse_agent_response(response_text)
    
    # If there was no response
    return AgentResponse(
        message="Sorry, I couldn't process your message. Could you please try again?",
        should_escalate=False
    )