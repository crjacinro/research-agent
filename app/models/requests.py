from pydantic import Field, BaseModel


class AgentCreate(BaseModel):
    name: str = Field(..., description="Name of the research agent")
