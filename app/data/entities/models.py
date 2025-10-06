from beanie import Document
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import Field

TIMEZONE_OFFSET = timezone(timedelta(hours=8))

class ConversationInDB(Document):
    id: str = Field(..., description="The conversation id")
    query: str = Field(..., description="The user query")
    agent_response: str = Field(..., description="The agent's response")
    source: str = Field(..., description="The source used for the response")
    documents: List[str] = Field(default_factory=list, description="List of documents used for the research")
    created_at: datetime = Field(default_factory=lambda: datetime.now(TIMEZONE_OFFSET))

    class Settings:
        name = "conversations"

class AgentInDB(Document):
    id: str = Field(..., description="The agent id")
    name: str = Field(..., description="The agent name")
    created_at: datetime = Field(default_factory=lambda: datetime.now(TIMEZONE_OFFSET))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(TIMEZONE_OFFSET))
    messages: Optional[List[ConversationInDB]] = Field(default_factory=list, description="List of conversation messages")

    class Settings:
        name = "agents"