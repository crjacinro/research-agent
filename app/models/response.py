from pydantic import Field, BaseModel

from app.data.entities.models import AgentInDB


class AgentOut(BaseModel):
    id: str = Field(..., description="Unique identifier for the research agent")
    name: str = Field(..., description="Name of the research agent")

class DocumentSourceOut(BaseModel):
    doc_id: str = Field(..., description="Document identifier from the source")
    doc_title: str = Field(..., description="Document title from the source")

class AgentQueryResponseOut(BaseModel):
    agent_id: str = Field(..., description="Unique identifier for the research agent")
    source: str = Field(..., description="Source of the document")
    response: str = Field(..., description="Response from the research agent to the query")

def agent_in_db_to_out(agent_in_db: AgentInDB) -> AgentOut:
    return AgentOut(id=agent_in_db.id, name=agent_in_db.name)
