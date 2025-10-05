from app.data.entities.models import AgentInDB
from app.models.requests import AgentCreate

async def create_agent_entity(agent_id: str, agent_in: AgentCreate) -> AgentInDB:
    new_agent = AgentInDB(id=agent_id, **agent_in.model_dump())
    await new_agent.insert()

    return new_agent

async def get_agent_entity(agent_id: str) -> AgentInDB:
    current_agent = await AgentInDB.find_one(AgentInDB.id == agent_id)
    if current_agent is None:
        raise KeyError(f"Agent with id {agent_id} does not exist and cannot be retrieved")

    return current_agent

async def delete_agent_entity(agent_id: str):
    agent_to_delete = await AgentInDB.find_one(AgentInDB.id == agent_id)
    if agent_to_delete is None:
        raise KeyError(f"Agent with id {agent_id} does not exist and cannot be deleted")

    await agent_to_delete.delete()


