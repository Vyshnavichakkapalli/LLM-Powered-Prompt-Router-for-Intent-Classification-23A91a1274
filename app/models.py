from pydantic import BaseModel, Field
from typing import Optional

class IntentLabel(BaseModel):
    intent: str = Field(description="The classified intent of the user (code, data, writing, career, unclear)")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    intent: str
    confidence: float
    response: str

class LogEntry(BaseModel):
    intent: str
    confidence: float
    user_message: str
    final_response: str
