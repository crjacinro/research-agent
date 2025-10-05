import pytest
from unittest.mock import AsyncMock, patch

from app.data.repositories.agent_repository import create_agent_entity, get_agent_entity, delete_agent_entity
from app.models.requests import AgentCreate

@pytest.mark.asyncio
async def test_create_agent_entity_success():
    """Test successful agent creation with database insertion."""
    agent_id = "test-agent-123"
    agent_name = "Test Agent"
    agent_create = AgentCreate(name=agent_name)
    
    with patch('app.data.repositories.agent_repository.AgentInDB') as mock_agent_class:
        mock_agent = AsyncMock()
        mock_agent.id = agent_id
        mock_agent.name = agent_name
        mock_agent.insert = AsyncMock()
        
        mock_agent_class.return_value = mock_agent
        
        result = await create_agent_entity(agent_id, agent_create)
        
        mock_agent_class.assert_called_once_with(
            id=agent_id,
            name=agent_name
        )
        
        mock_agent.insert.assert_called_once()
        
        assert result == mock_agent

@pytest.mark.asyncio
async def test_get_agent_entity_success():
    """Test successful agent retrieval."""
    agent_id = "test-agent-123"
    agent_name = "Test Agent"
    
    mock_agent = AsyncMock()
    mock_agent.id = agent_id
    mock_agent.name = agent_name
    
    with patch('app.data.repositories.agent_repository.AgentInDB') as mock_agent_class:
        mock_agent_class.find_one = AsyncMock(return_value=mock_agent)
        
        result = await get_agent_entity(agent_id)
        
        mock_agent_class.find_one.assert_called_once_with(mock_agent_class.id == agent_id)

        assert result == mock_agent

@pytest.mark.asyncio
async def test_get_agent_entity_not_found():
    """Test agent retrieval when agent does not exist."""
    agent_id = "non-existent-agent"
    
    with patch('app.data.repositories.agent_repository.AgentInDB') as mock_agent_class:
        mock_agent_class.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(KeyError) as exc_info:
            await get_agent_entity(agent_id)
        
        assert f"Agent with id {agent_id} does not exist and cannot be retrieved" in str(exc_info.value)

@pytest.mark.asyncio
async def test_delete_agent_entity_success():
    """Test successful agent deletion."""
    agent_id = "test-agent-123"
    
    mock_agent = AsyncMock()
    mock_agent.id = agent_id
    mock_agent.delete = AsyncMock()
    
    with patch('app.data.repositories.agent_repository.AgentInDB') as mock_agent_class:
        mock_agent_class.find_one = AsyncMock(return_value=mock_agent)
        
        await delete_agent_entity(agent_id)
        
        mock_agent_class.find_one.assert_called_once_with(mock_agent_class.id == agent_id)
        
        mock_agent.delete.assert_called_once()

@pytest.mark.asyncio
async def test_delete_agent_entity_not_found():
    """Test agent deletion when agent does not exist."""
    agent_id = "non-existent-agent"
    
    with patch('app.data.repositories.agent_repository.AgentInDB') as mock_agent_class:
        mock_agent_class.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(KeyError) as exc_info:
            await delete_agent_entity(agent_id)
        
        assert f"Agent with id {agent_id} does not exist and cannot be deleted" in str(exc_info.value)
