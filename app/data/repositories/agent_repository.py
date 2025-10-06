from uuid import uuid4

from app.data.entities.models import AgentInDB, ConversationInDB, TIMEZONE_OFFSET
from app.models.results import QueryResult
from app.models.requests import AgentCreate
from datetime import datetime

async def create_agent_entity(agent_in: AgentCreate) -> AgentInDB:
    new_agent = AgentInDB(id=str(uuid4()), **agent_in.model_dump())
    await new_agent.insert()

    return new_agent

async def get_agent_entity(agent_id: str) -> AgentInDB:
    current_agent = await AgentInDB.find_one(AgentInDB.id == agent_id)
    if current_agent is None:
        raise KeyError(f"Agent with id {agent_id} does not exist and cannot be retrieved")

    return current_agent

async def delete_agent_entity(agent_id: str):
    agent_to_delete = await get_agent_entity(agent_id)

    await agent_to_delete.delete()

async def add_conversations(agent_id: str, query: str, query_result: QueryResult):
    current_agent = await get_agent_entity(agent_id)

    new_conversation = ConversationInDB(
        id=str(uuid4()),
        query=query,
        agent_response=query_result.agent_response,
        source=query_result.domain,
        documents=query_result.documents
    )
    
    current_agent.messages.append(new_conversation)
    current_agent.updated_at = datetime.now(TIMEZONE_OFFSET)
    
    await current_agent.save()
