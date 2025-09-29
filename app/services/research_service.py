from typing import Any, Coroutine

from app.models.requests import AgentCreate
from app.models.response import AgentOut
from uuid import uuid4

AGENTS = {}

async def get_agent(agent_id: str) -> AgentOut:
    if agent_id not in AGENTS:
        raise KeyError(f"Agent with id {agent_id} does not exist and cannot be retrieved")
    return AGENTS[agent_id]

async def create_agent(agent_in: AgentCreate) -> AgentOut:
    agent_id = str(uuid4())
    agent = AgentOut(id=agent_id, **agent_in.model_dump())
    AGENTS[agent_id] = agent
    return agent

async def delete_agent(agent_id: str):
    agent = AGENTS.pop(agent_id, None)
    if agent is None:
        raise KeyError(f"Agent with id {agent_id} does not exist and cannot be deleted")
