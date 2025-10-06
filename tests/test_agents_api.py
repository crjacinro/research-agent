import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.agents import router as agents_router


def create_test_app() -> TestClient:
    app = FastAPI()
    app.include_router(agents_router)
    return TestClient(app)


@pytest.fixture()
def client():
    return create_test_app()


def test_create_agent_success(client, monkeypatch):
    from app.models.response import AgentOut

    async def fake_create_agent(agent_in):
        return AgentOut(id="abc123", name=agent_in.name)

    monkeypatch.setattr("app.services.research_service.create_agent", fake_create_agent)

    payload = {"name": "Researcher"}
    response = client.post("/agents/", json=payload)

    assert response.status_code == 201
    assert response.json() == {"id": "abc123", "name": "Researcher", "messages": []}


def test_create_agent_validation_error_returns_400(client, monkeypatch):
    async def fake_create_agent(agent_in):
        raise ValueError("invalid agent data")

    monkeypatch.setattr("app.services.research_service.create_agent", fake_create_agent)

    payload = {"name": "BadAgent"}
    response = client.post("/agents/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid agent data"


def test_get_agent_success(client, monkeypatch):
    from app.models.response import AgentOut

    async def fake_get_agent(agent_id: str):
        return AgentOut(id=agent_id, name="A1")

    monkeypatch.setattr("app.services.research_service.get_agent", fake_get_agent)

    response = client.get("/agents/xyz")

    assert response.status_code == 200
    assert response.json() == {"id": "xyz", "name": "A1", "messages": []}


def test_get_agent_not_found_returns_404(client, monkeypatch):
    async def fake_get_agent(agent_id: str):
        raise KeyError('agent not found')

    monkeypatch.setattr("app.services.research_service.get_agent", fake_get_agent)

    response = client.get("/agents/missing")


    assert response.status_code == 404
    assert response.json()["detail"] == 'agent not found'


def test_delete_agent_success_returns_204(client, monkeypatch):
    async def fake_delete_agent(agent_id: str):
        return None

    monkeypatch.setattr("app.services.research_service.delete_agent", fake_delete_agent)

    response = client.delete("/agents/abc")

    assert response.status_code == 204


def test_delete_agent_not_found_returns_404(client, monkeypatch):
    async def fake_delete_agent(agent_id: str):
        raise KeyError("agent not found")

    monkeypatch.setattr("app.services.research_service.delete_agent", fake_delete_agent)

    response = client.delete("/agents/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "agent not found"


def test_send_queries_success(client, monkeypatch):
    from app.models.results import QueryResult
    
    async def fake_send_queries(agent_id: str, message: str):
        return QueryResult(
            agent_response="Research response",
            domain="arxiv",
            documents=["doc1.pdf", "doc2.pdf"]
        )

    monkeypatch.setattr("app.services.research_service.send_queries", fake_send_queries)

    payload = {"message": "What is machine learning?"}
    response = client.post("/agents/abc123/queries", json=payload)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["agent_id"] == "abc123"
    assert response_data["response"] == "Research response"
    assert response_data["domain"] == "arxiv"
    assert response_data["documents"] == ["doc1.pdf", "doc2.pdf"]


def test_send_queries_validation_error_returns_400(client, monkeypatch):
    async def fake_send_queries(agent_id: str, message: str):
        raise ValueError("Invalid query message")

    monkeypatch.setattr("app.services.research_service.send_queries", fake_send_queries)

    payload = {"message": ""}
    response = client.post("/agents/abc123/queries", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid query message"


