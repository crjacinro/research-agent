from beanie import Document


class AgentInDB(Document):
    id: str
    name: str

    class Settings:
        name = "agents"