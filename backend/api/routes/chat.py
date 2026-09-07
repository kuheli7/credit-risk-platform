from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])
chat_service = ChatService()

class ChatQueryRequest(BaseModel):
    question: str = Field(..., example="What is the default rate by income type?")
    session_id: Optional[str] = Field(None, example="user_session_123")

class ClearChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, example="user_session_123")

@router.get("/samples")
def get_sample_queries():
    """Returns sample analytical questions."""
    return {"samples": chat_service.get_sample_questions()}

@router.post("")
def query_data(payload: ChatQueryRequest):
    """Processes a natural language query into SQL, executes it, and synthesizes executive findings."""
    result = chat_service.process_query(payload.question)
    return result

@router.post("/clear")
def clear_chat(payload: Optional[ClearChatRequest] = None):
    """Resets conversational memory and context."""
    sid = payload.session_id if payload else None
    chat_service.clear_history(sid)
    return {"success": True, "message": "Conversation history cleared."}
