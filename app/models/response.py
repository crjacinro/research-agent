from pydantic import Field, BaseModel

from app.data.entities.models import AgentInDB


class AgentOut(BaseModel):
    id: str = Field(..., description="Unique identifier for the research agent")
    name: str = Field(..., description="Name of the research agent")


def agent_in_db_to_out(agent_in_db: AgentInDB) -> AgentOut:
    return AgentOut(id=agent_in_db.id, name=agent_in_db.name)
