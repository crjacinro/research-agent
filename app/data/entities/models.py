from beanie import Document
from datetime import datetime, timezone, timedelta

class AgentInDB(Document):
    id: str
    name: str
    created_at: datetime = datetime.now(timezone(timedelta(hours=8)))
    updated_at: datetime = datetime.now(timezone(timedelta(hours=8)))

    class Settings:
        name = "agents"