from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

# --- SQLModel Tables (DB) ---

class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    name: Optional[str] = Field(default="New Chat")

    messages: List["ChatMessage"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chatsession.id")
    role: str  # 'user', 'assistant'
    content: str

    # Billing fields
    model_name: str = Field(default="gpt-4o-mini")
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    cost_usd: float = Field(default=0.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    session: Optional["ChatSession"] = Relationship(back_populates="messages")



class ChatRequest(BaseModel):
    user_input: str
