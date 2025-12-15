# Servicio para comunicación con WhatsApp via SpicyTool API

import os
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

# Configuración desde variables de entorno
SPICYTOOL_API_URL = os.getenv("SPICYTOOL_API_URL", "https://api.spicytool.net/api/webhooks/whatsApp/sendMessage")
SPICY_API_TOKEN = os.getenv("SPICY_API_TOKEN")


async def send_whatsapp_message(user_email: str, conversation_id: str, message: str) -> dict:
    """
    Envía un mensaje a WhatsApp a través de la API de SpicyTool.
    """
    payload = {
        "userEmail": user_email,
        "conversationId": conversation_id,
        "message": message
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-webhook-token": SPICY_API_TOKEN
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SPICYTOOL_API_URL,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text
            }
    except httpx.TimeoutException:
        return {
            "success": False,
            "status_code": 408,
            "response": "Timeout connecting to SpicyTool API"
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "response": str(e)
        }


def validate_config() -> bool:
    """Valida que las variables de entorno estén configuradas."""
    if not SPICY_API_TOKEN:
        print("⚠️ WARNING: SPICY_API_TOKEN not set in .env")
        return False
    return True