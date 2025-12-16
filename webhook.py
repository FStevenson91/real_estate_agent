# FastAPI server to receive WhatsApp messages

from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from dotenv import load_dotenv

from models import WebhookPayload, WebhookResponse
from services import validate_config, debouncer, process_and_respond

load_dotenv(override=True)

# Debounce delay in seconds
DEBOUNCE_DELAY = 7.0

# LIFESPAN (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on application startup and shutdown.
    - Code BEFORE the yield = startup
    - Code AFTER the yield = shutdown
    """

    # STARTUP
    print("🚀 Starting Real Estate Agent Webhook...")
    print("⏱️  Debounce delay: " + str(DEBOUNCE_DELAY) + " seconds")
    
    if not validate_config():
        print("⚠️ Configuration incomplete. Check your .env file.")
    else:
        print("✅ Configuration loaded successfully")
    
    print("📍 Webhook ready at: /webhook/whatsapp")
    print("📚 Docs available at: /docs")
    
    yield  # app runs here
    
    # SHUTDOWN
    print("👋 Shutting down webhook...")
    await debouncer.cancel_all()


# Create APP
app = FastAPI(
    title="Real Estate Agent Webhook",
    description="Webhook to receive WhatsApp messages and respond using the real estate agent",
    version="1.0.0",
    lifespan=lifespan
)

# ENDPOINTS
@app.post("/webhook/whatsapp", response_model=WebhookResponse)
async def receive_whatsapp_message(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Receives WhatsApp messages from SpicyTool,
    processes them with the real estate agent,
    and sends the response back to WhatsApp.

    Uses debouncing to handle rapid consecutive messages.

    Flow:
    1. Receive message
    2. Add to debounce queue
    3. Return immediately (202 Accepted)
    4. After delay, process all buffered messages together
    5. Send single response to WhatsApp
    """
    # 1. Extract the user's message (fromMe = false)
    user_messages = [msg for msg in payload.conversation if not msg.fromMe]
    
    if not user_messages:
        return {"status": "no_user_message"}
    
    # 2. Get last message
    last_message = user_messages[-1]
    phone_number = payload.from_
    
    print("📩 Message from " + phone_number + ": " + last_message.body)
    
     # Check if already debouncing
    if debouncer.is_pending(phone_number):
        print("⏳ Adding to debounce buffer for " + phone_number)
    else:
        print("⏳ Starting debounce timer for " + phone_number)
    
    # Prepare payload data for callback
    payload_data = {
        "userEmail": payload.userEmail,
        "contactId": payload.contactId,
        "assignedContainer": payload.assignedContainer
    }
    
    # Add to debouncer (non-blocking)
    await debouncer.debounce(
        phone_number=phone_number,
        message_text=last_message.body,
        payload_data=payload_data,
        process_callback=process_and_respond
    )
    
    # Return immediately
    return {
        "status": "debouncing",
        "message": "Message received, waiting for more messages...",
        "phone_number": phone_number,
        "pending_count": debouncer.get_pending_count()
    }


@app.post("/webhook/whatsapp/sync", response_model=WebhookResponse)
async def receive_whatsapp_message_sync(payload: WebhookPayload):
    """
    Synchronous version - waits for debounce and returns response.
    Use this for testing or when you need immediate response.
    """
    
    # Extract user messages
    user_messages = [msg for msg in payload.conversation if not msg.fromMe]
    
    if not user_messages:
        return WebhookResponse(status="no_user_message")
    
    last_message = user_messages[-1]
    phone_number = payload.from_
    
    print("📩 [SYNC] Message from " + phone_number + ": " + last_message.body)
    
    payload_data = {
        "userEmail": payload.userEmail,
        "contactId": payload.contactId,
        "assignedContainer": payload.assignedContainer
    }
    
    # Debounce and wait for result
    result = await debouncer.debounce_and_wait(
        phone_number=phone_number,
        message_text=last_message.body,
        payload_data=payload_data,
        process_callback=process_and_respond
    )
    
    # If superseded by newer message
    if result is None:
        return WebhookResponse(
            status="superseded",
            message_sent=None,
            should_escalate=False
        )
    
    # Return full response
    agent_response = result["agent_response"]
    whatsapp_result = result["whatsapp_result"]
    
    response = WebhookResponse(
        status="success" if whatsapp_result["success"] else "error",
        message_sent=agent_response.message,
        whatsapp_api_status=whatsapp_result["status_code"],
        should_escalate=agent_response.should_escalate
    )
    
    if agent_response.should_escalate:
        response.escalation = {
            "reason": "User requested human assistance",
            "contact": phone_number
        }
    
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "real_estate_agent_webhook",
        "version": "1.0.0",
        "debounce_delay_seconds": DEBOUNCE_DELAY,
        "pending_messages": debouncer.get_pending_count()
    }


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "Real Estate Agent Webhook",
        "features": ["debouncing", "escalation", "BANT qualification"],
        "endpoints": {
            "webhook_async": "POST /webhook/whatsapp (non-blocking, recommended)",
            "webhook_sync": "POST /webhook/whatsapp/sync (blocking, for testing)",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }

# RUN LOCALLY
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)