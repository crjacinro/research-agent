from uuid import UUID

import pytest

from app.models.requests import AgentCreate
from app.services import research_service

@pytest.mark.asyncio
async def test_create_agent_success(monkeypatch):
    agent_name = "Research Agent"
    agent_uuid = UUID("00000000-0000-0000-0000-000000000000")
    insert_called = False
    class FakeAgent:
        def __init__(self, id: str, name: str):
            self.id = id
            self.name = name
        async def insert(self):
            nonlocal insert_called
            insert_called = True

    def fake_constructor(id: str, name: str):
        return FakeAgent(id=id, name=name)
    monkeypatch.setattr(research_service, "AgentInDB", fake_constructor)
    monkeypatch.setattr(research_service, "uuid4", lambda: agent_uuid)

    result = await research_service.create_agent(AgentCreate(name=agent_name))

    assert insert_called is True
    assert result.id == str(agent_uuid)
    assert result.name == agent_name


@pytest.mark.asyncio
async def test_get_agent_success(monkeypatch):
    agent_id = "agent-id-123"
    agent_name = "Agent 123"
    class FakeAgent:
        def __init__(self, id: str, name: str):
            self.id = id
            self.name = name
    class AgentInDBProxy:
        id = None  # placeholder to allow attribute access in expression
        @staticmethod
        async def find_one(_):
            return FakeAgent(id=agent_id, name=agent_name)
    monkeypatch.setattr(research_service, "AgentInDB", AgentInDBProxy)

    result = await research_service.get_agent(agent_id)

    assert result.id == agent_id
    assert result.name == agent_name


@pytest.mark.asyncio
async def test_get_agent_not_found_raises_key_error(monkeypatch):
    class AgentInDBProxy:
        id = None

        @staticmethod
        async def find_one(_):
            return None
    monkeypatch.setattr(research_service, "AgentInDB", AgentInDBProxy)

    with pytest.raises(KeyError) as exc:
        await research_service.get_agent("missing")

    assert "does not exist and cannot be retrieved" in str(exc.value)


@pytest.mark.asyncio
async def test_delete_agent_success(monkeypatch):
    deleted = False
    class FakeAgent:
        async def delete(self):
            nonlocal deleted
            deleted = True
    class AgentInDBProxy:
        id = None
        @staticmethod
        async def find_one(_):
            return FakeAgent()
    monkeypatch.setattr(research_service, "AgentInDB", AgentInDBProxy)

    await research_service.delete_agent("abc123")

    assert deleted is True


@pytest.mark.asyncio
async def test_delete_agent_missing_raises_key_error(monkeypatch):
    class AgentInDBProxy:
        id = None
        @staticmethod
        async def find_one(_):
            return None
    monkeypatch.setattr(research_service, "AgentInDB", AgentInDBProxy)

    with pytest.raises(KeyError) as exc:
        await research_service.delete_agent("missing")

    assert "does not exist and cannot be deleted" in str(exc.value)


@pytest.mark.asyncio
async def test_send_queries_success(monkeypatch):
    agent_id = "agent-id-123"
    query = "What is machine learning?"
    expected_answer = "Machine learning is a subset of artificial intelligence..."
    expected_domain = "research"
    
    class FakeAgent:
        def __init__(self, id: str):
            self.id = id
    
    class AgentInDBProxy:
        id = None
        @staticmethod
        async def find_one(_):
            return FakeAgent(id=agent_id)
    
    def mock_process_query(query: str):
        return expected_answer, expected_domain
    
    monkeypatch.setattr(research_service, "AgentInDB", AgentInDBProxy)
    monkeypatch.setattr(research_service, "process_query", mock_process_query)
    
    result = await research_service.send_queries(agent_id, query)
    
    assert result == (expected_answer, expected_domain)


@pytest.mark.asyncio
async def test_send_queries_agent_not_found_raises_value_error(monkeypatch):
    agent_id = "missing-agent"
    query = "What is machine learning?"
    
    class AgentInDBProxy:
        id = None
        @staticmethod
        async def find_one(_):
            return None
    
    monkeypatch.setattr(research_service, "AgentInDB", AgentInDBProxy)
    
    with pytest.raises(ValueError) as exc:
        await research_service.send_queries(agent_id, query)
    
    assert f"Agent with id {agent_id} does not exist" in str(exc.value)


@pytest.mark.asyncio
async def test_send_queries_empty_query_raises_value_error(monkeypatch):
    agent_id = "agent-id-123"
    
    class FakeAgent:
        def __init__(self, id: str):
            self.id = id
    
    class AgentInDBProxy:
        id = None
        @staticmethod
        async def find_one(_):
            return FakeAgent(id=agent_id)
    
    monkeypatch.setattr(research_service, "AgentInDB", AgentInDBProxy)
    
    with pytest.raises(ValueError) as exc:
        await research_service.send_queries(agent_id, "")
    
    assert "Query message must be a non-empty string" in str(exc.value)
