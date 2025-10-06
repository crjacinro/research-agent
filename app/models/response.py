from typing import Optional, List

from pydantic import Field, BaseModel

from app.data.entities.models import AgentInDB, ConversationInDB


class ConversationsOut(BaseModel):
    id: str = Field(..., description="Unique identifier for the conversation")
    query: str = Field(..., description="The user query")
    agent_response: str = Field(..., description="The agent's response")
    domain: str = Field(..., description="The domain of the query")
    documents: list[str] = Field(default_factory=list, description="List of documents used for the research")

class AgentOut(BaseModel):
    id: str = Field(..., description="Unique identifier for the research agent")
    name: str = Field(..., description="Name of the research agent")
    messages: Optional[List[ConversationsOut]] = Field(default_factory=list, description="List of conversation messages")

class AgentQueryResponseOut(BaseModel):
    agent_id: str = Field(..., description="Unique identifier for the research agent")
    domain: str = Field(..., description="Domain based on the query type")
    documents: list[str] = Field(..., description="List of documents used by the source")
    response: str = Field(..., description="Response from the research agent to the query")

def agent_in_db_to_out(agent_in_db: AgentInDB) -> AgentOut:
    return AgentOut(id=agent_in_db.id,
                    name=agent_in_db.name,
                    messages=list_conversation_in_db_to_out(agent_in_db.messages))

def list_conversation_in_db_to_out(
        conversations_in_db: Optional[List[ConversationInDB]]
) -> List[ConversationsOut]:
    if conversations_in_db is None:
        return []
    return [conversation_in_db_to_out(conversation) for conversation in conversations_in_db]

def conversation_in_db_to_out(
        conversation_in_db: ConversationInDB
) -> ConversationsOut:
    return ConversationsOut(
        id = conversation_in_db.id,
        query=conversation_in_db.query,
        agent_response=conversation_in_db.agent_response,
        domain=conversation_in_db.source,
        documents=conversation_in_db.documents
    )