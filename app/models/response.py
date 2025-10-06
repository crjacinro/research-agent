from pydantic import Field, BaseModel

from app.data.entities.models import AgentInDB


class AgentOut(BaseModel):
    id: str = Field(..., description="Unique identifier for the research agent")
    name: str = Field(..., description="Name of the research agent")

class AgentQueryResponseOut(BaseModel):
    agent_id: str = Field(..., description="Unique identifier for the research agent")
    domain: str = Field(..., description="Domain based on the query type")
    documents: list[str] = Field(..., description="List of documents used by the source")
    response: str = Field(..., description="Response from the research agent to the query")

def agent_in_db_to_out(agent_in_db: AgentInDB) -> AgentOut:
    return AgentOut(id=agent_in_db.id, name=agent_in_db.name)
