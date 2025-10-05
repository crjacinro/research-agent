import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.data.entities.models import AgentInDB, ConversationInDB

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

async def init_db():
    """
    Initialize MongoDB client and Beanie document models.
    """
    global _client, _db

    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db = os.getenv("MONGODB_DB")

    _client = AsyncIOMotorClient(mongodb_uri)
    _db = _client[mongodb_db]

    await init_beanie(database=_db, document_models=[AgentInDB, ConversationInDB])

    print("✅ MongoDB + Beanie initialized.")

async def close_db():
    """
    Close MongoDB client on app shutdown.
    """
    global _client
    if _client:
        _client.close()
        print("🛑 MongoDB connection closed.")