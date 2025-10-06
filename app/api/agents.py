from fastapi import APIRouter, HTTPException, status

from app.models.requests import AgentCreate, AgentQueries
from app.models.response import AgentOut, AgentQueryResponseOut
from app.services import research_service

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_in: AgentCreate):
    """
    Create a new research agent definition.
    """
    try:
        agent = await research_service.create_agent(agent_in)
        return agent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(agent_id: str):
    """
    Returns a research agent specified by the id.
    """
    try:
        agents = await research_service.get_agent(agent_id)
        return agents
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.args[0] if e.args else str(e)
        )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str):
    """
    Deletes a research agent specified by the id.
    """
    try:
        await research_service.delete_agent(agent_id)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.args[0] if e.args else str(e)
        )

@router.post("/{agent_id}/queries", response_model=AgentQueryResponseOut, status_code=status.HTTP_201_CREATED)
async def send_queries(agent_id: str, query: AgentQueries):
    """
    Sends new queries for the agent specified.
    """
    try:
        query_result = await research_service.send_queries(agent_id, query.message)
        return AgentQueryResponseOut(agent_id=agent_id,
                                     response=query_result.agent_response,
                                     domain=query_result.domain,
                                     documents=query_result.documents)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )