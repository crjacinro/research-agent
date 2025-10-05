from app.data.repositories.agent_repository import create_agent_entity, delete_agent_entity, get_agent_entity
from app.models.requests import AgentCreate
from app.models.response import AgentOut, agent_in_db_to_out
from uuid import uuid4
from app.workflows.research_graph import process_query

async def get_agent(agent_id: str) -> AgentOut:
    current_agent = await get_agent_entity(agent_id)

    return agent_in_db_to_out(current_agent)

async def create_agent(agent_in: AgentCreate) -> AgentOut:
    agent_id = str(uuid4())
    new_agent = await create_agent_entity(agent_id, agent_in)

    return agent_in_db_to_out(new_agent)

async def delete_agent(agent_id: str):
    await delete_agent_entity(agent_id)

async def send_queries(agent_id: str, query: str) -> tuple[str, str, list[str]]:
    if not query or not query.strip():
        raise ValueError("Query message must be a non-empty string")

    current_agent = await get_agent_entity(agent_id)

    return process_query(query)
