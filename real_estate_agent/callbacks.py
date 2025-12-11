from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from .prompt import agent_prompt_template
from .config import AGENT_NAME, COMPANY, PERSONALITY, DEFAULTS
from .tools.crm import get_contact
from .tools.location import detect_location


def get_contact_context(phone_number: str = None) -> dict:
    """
    Get contact info from CRM
    Returns context and greeting instruction
    """
    if phone_number:
        result = get_contact(phone_number)

        if result["status"] == "success" and result.get("contact"):
            contact = result["contact"]
            name = contact.get("name", "")
            contact_context = "Existing contact. Name: " + name
            greeting_instruction = "This is a returning contact named " + name + ". Greet them by name. Do NOT ask for their name again."
            return {
                "contact_context": contact_context, 
                "greeting_instruction": greeting_instruction,
                "is_new": False,
                "phone_number": phone_number
            }
    
    contact_context = "New contact. Not in CRM yet."
    greeting_instruction = "This is a new contact. Say: '¡Hola! Soy [your name], asesor inmobiliario de [company]. ¿Cuál es tu nombre y cómo puedo ayudarte?' Before scheduling, you MUST ask for their email. After scheduling, use create_contact tool with their full name, email, and phone number: " + str(phone_number) + "."
    return {
        "contact_context": contact_context, 
        "greeting_instruction": greeting_instruction,
        "is_new": True,
        "phone_number": phone_number
    }

    
def get_location_context() -> dict:
    """
    Detecta la ubicación del usuario.
    """
    result = detect_location()
    
    if result["status"] == "success":
        return {
            "detected_country": result.get("country", "Unknown")
        }
    
    return {
        "detected_country": "Unknown"
    }


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    """Runs before sending the request to the LLM. Hidrates the template"""

    phone_number = callback_context.state.get("user_id", None)
    crm_data = get_contact_context(phone_number)
    location_data = get_location_context()

    final_instruction = agent_prompt_template.format(
        agent_name=AGENT_NAME or DEFAULTS["agent_name"],
        company=COMPANY or DEFAULTS["company"],
        personality=PERSONALITY or DEFAULTS["personality"],
        contact_context=crm_data["contact_context"],
        greeting_instruction=crm_data["greeting_instruction"],
        detected_country=location_data["detected_country"]
    )

    if llm_request.config:
        llm_request.config.system_instruction = final_instruction

    return None