from pydantic import Field, BaseModel


class AgentOut(BaseModel):
    id: str = Field(..., description="Unique identifier for the research agent")
    name: str = Field(..., description="Name of the research agent")
