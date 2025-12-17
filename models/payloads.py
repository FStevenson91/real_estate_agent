# Pydantic models for input and output payloads

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union


class Message(BaseModel):
    """Individual message in the WhatsApp conversation."""
    id: str = ""
    body: str = ""
    fromMe: bool = False
    timestamp: int = 0

    @field_validator('timestamp', mode='before')
    @classmethod
    def convert_timestamp(cls, v):
        """Convert timestamp to int, handling floats and strings."""
        if v is None:
            return 0
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return 0

    @field_validator('fromMe', mode='before')
    @classmethod
    def convert_from_me(cls, v):
        """Convert fromMe to bool."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes')
        return bool(v)


class WebhookPayload(BaseModel):
    """Payload we receive from SpicyTool when a WhatsApp message arrives."""
    chatBotId: str = ""
    userEmail: str = ""
    clientNumber: str = ""
    from_: str = Field(default="", alias="from")  # "from" is a reserved word in Python
    contactId: str = ""
    assignedContainer: str = ""
    conversation: List[Message] = Field(default_factory=list)

    class Config:
        populate_by_name = True

    @field_validator('chatBotId', 'userEmail', 'clientNumber', 'contactId', 'assignedContainer', mode='before')
    @classmethod
    def convert_to_string(cls, v):
        """Convert any value to string, handling None and ObjectId-like objects."""
        if v is None:
            return ""
        if isinstance(v, dict) and '$oid' in v:
            return v['$oid']
        return str(v)


class WhatsAppOutgoingMessage(BaseModel):
    """Payload to send a message to WhatsApp via SpicyTool."""
    userEmail: str
    conversationId: str
    message: str


class AgentResponse(BaseModel):
    """Parsed agent response."""
    message: str
    should_escalate: bool = False


class WebhookResponse(BaseModel):
    """Response returned by our webhook."""
    status: str
    message_sent: Optional[str] = None
    whatsapp_api_status: Optional[int] = None
    should_escalate: bool = False
    escalation: Optional[dict] = None
