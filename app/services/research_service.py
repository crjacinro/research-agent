from app.data.entities.models import AgentInDB
from app.models.requests import AgentCreate
from app.models.response import AgentOut, agent_in_db_to_out
from uuid import uuid4
from app.workflows.research_graph import build_research_graph, process_query


async def get_agent(agent_id: str) -> AgentOut:
    current_agent = await AgentInDB.find_one(AgentInDB.id == agent_id)
    if current_agent is None:
        raise KeyError(f"Agent with id {agent_id} does not exist and cannot be retrieved")

    return agent_in_db_to_out(current_agent)

async def create_agent(agent_in: AgentCreate) -> AgentOut:
    agent_id = str(uuid4())
    new_agent = AgentInDB(id=agent_id, **agent_in.model_dump())

    await new_agent.insert()

    return agent_in_db_to_out(new_agent)


async def delete_agent(agent_id: str):
    agent_to_delete = await AgentInDB.find_one(AgentInDB.id == agent_id)
    if agent_to_delete is None:
        raise KeyError(f"Agent with id {agent_id} does not exist and cannot be deleted")

    await agent_to_delete.delete()

async def send_queries(agent_id: str, query: str) -> tuple[str, str]:
    current_agent = await AgentInDB.find_one(AgentInDB.id == agent_id)
    if current_agent is None:
        raise ValueError(f"Agent with id {agent_id} does not exist")

    if not query or not query.strip():
        raise ValueError("Query message must be a non-empty string")

    return process_query(query)
