# Modelos Pydantic para los payloads de entrada y salida

from pydantic import BaseModel, Field
from typing import List, Optional


class Message(BaseModel):
    """Mensaje individual de la conversación de WhatsApp."""
    id: str
    body: str
    fromMe: bool
    timestamp: int


class WebhookPayload(BaseModel):
    """
    Payload que recibimos de SpicyTool cuando llega un mensaje de WhatsApp.
    """
    chatBotId: str
    userEmail: str
    clientNumber: str
    from_: str = Field(alias="from")  # "from" es palabra reservada en Python
    contactId: str
    assignedContainer: str
    conversation: List[Message]

    class Config:
        populate_by_name = True


class WhatsAppOutgoingMessage(BaseModel):
    """Payload para enviar mensaje a WhatsApp via SpicyTool."""
    userEmail: str
    conversationId: str
    message: str


class AgentResponse(BaseModel):
    """Respuesta parseada del agente."""
    message: str
    should_escalate: bool = False


class WebhookResponse(BaseModel):
    """Respuesta que devuelve nuestro webhook."""
    status: str
    message_sent: Optional[str] = None
    whatsapp_api_status: Optional[int] = None
    should_escalate: bool = False
    escalation: Optional[dict] = None