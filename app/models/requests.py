from pydantic import Field, BaseModel


class AgentCreate(BaseModel):
    name: str = Field(..., description="Name of the research agent")

class AgentQueries(BaseModel):
    message: str = Field(..., description="The query message to be sent to the agent")
