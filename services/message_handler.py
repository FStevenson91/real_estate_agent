# Handler for processing messages and sending responses

from .agent_runner import process_message
from .whatsapp import send_whatsapp_message


async def process_and_respond(phone_number: str, message_text: str, payload_data: dict) -> dict:
    """
    Process message with agent and send response to WhatsApp.
    This is called after debounce delay.
    
    Args:
        phone_number: User phone number
        message_text: Combined message text (after debounce)
        payload_data: Additional data (userEmail, contactId, etc)
        
    Returns:
        dict with agent_response and whatsapp_result
    """
    print("🔄 Processing debounced message from " + phone_number + ": " + message_text)
    
    # Process with agent
    agent_response = await process_message(
        phone_number=phone_number,
        message_text=message_text
    )
    
    print("🤖 Agent response: " + agent_response.message[:50] + "...")
    
    # Send response to WhatsApp
    whatsapp_result = await send_whatsapp_message(
        user_email=payload_data.get("userEmail", ""),
        conversation_id=phone_number,
        message=agent_response.message
    )
    
    # Log result
    if whatsapp_result["success"]:
        print("✅ Message sent to " + phone_number)
    else:
        print("❌ Failed to send message: " + str(whatsapp_result["status_code"]))
    
    # Handle escalation
    if agent_response.should_escalate:
        print("⚠️ ESCALATION NEEDED for " + phone_number)
        # TODO: Notify human agent (Slack, email, CRM, etc.)
    
    return {
        "agent_response": agent_response,
        "whatsapp_result": whatsapp_result
    }