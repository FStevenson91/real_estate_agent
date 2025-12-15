# Servidor FastAPI para recibir mensajes de WhatsApp

from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from models import WebhookPayload, WebhookResponse
from services import send_whatsapp_message, process_message, validate_config

load_dotenv(override=True)


# LIFESPAN (reemplaza on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta al iniciar y cerrar la aplicación.
    - Código ANTES del yield = startup
    - Código DESPUÉS del yield = shutdown
    """
    # STARTUP
    print("🚀 Starting Real Estate Agent Webhook...")
    
    if not validate_config():
        print("⚠️ Configuration incomplete. Check your .env file.")
    else:
        print("✅ Configuration loaded successfully")
    
    print("📍 Webhook ready at: /webhook/whatsapp")
    print("📚 Docs available at: /docs")
    
    yield  # La app corre aquí
    
    # SHUTDOWN
    print("👋 Shutting down webhook...")


# Crear la APP
app = FastAPI(
    title="Real Estate Agent Webhook",
    description="Webhook para recibir mensajes de WhatsApp y responder con el agente inmobiliario",
    version="1.0.0",
    lifespan=lifespan
)


# ENDPOINTS

@app.post("/webhook/whatsapp", response_model=WebhookResponse)
async def receive_whatsapp_message(payload: WebhookPayload):
    """
    Recibe mensajes de WhatsApp desde SpicyTool,
    los procesa con el agente inmobiliario,
    y envía la respuesta de vuelta a WhatsApp.
    """
    
    # 1. Extraer el último mensaje del usuario (no fromMe)
    user_messages = [msg for msg in payload.conversation if not msg.fromMe]
    
    if not user_messages:
        return WebhookResponse(status="no_user_message")
    
    last_message = user_messages[-1]
    phone_number = payload.from_
    
    print("📩 Message from " + phone_number + ": " + last_message.body)
    
    # 2. Procesar mensaje con el agente
    agent_response = await process_message(
        phone_number=phone_number,
        message_text=last_message.body
    )
    
    print("🤖 Agent response: " + agent_response.message[:50] + "...")
    print("🚨 Should escalate: " + str(agent_response.should_escalate))
    
    # 3. Enviar respuesta a WhatsApp
    whatsapp_result = await send_whatsapp_message(
        user_email=payload.userEmail,
        conversation_id=phone_number,
        message=agent_response.message
    )
    
    # 4. Preparar respuesta
    response = WebhookResponse(
        status="success" if whatsapp_result["success"] else "error",
        message_sent=agent_response.message,
        whatsapp_api_status=whatsapp_result["status_code"],
        should_escalate=agent_response.should_escalate
    )
    
    # 5. Agregar info de escalación si corresponde
    if agent_response.should_escalate:
        response.escalation = {
            "reason": "User requested human assistance",
            "contact": phone_number,
            "contact_id": payload.contactId,
            "email": payload.userEmail,
            "assigned_container": payload.assignedContainer
        }
        print("⚠️ ESCALATION NEEDED for " + phone_number)
    
    return response


@app.get("/health")
async def health_check():
    """Endpoint para verificar que el servidor está activo."""
    return {
        "status": "ok",
        "service": "real_estate_agent_webhook",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Endpoint raíz con información del servicio."""
    return {
        "service": "Real Estate Agent Webhook",
        "endpoints": {
            "webhook": "POST /webhook/whatsapp",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


# Para correr localmente

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)