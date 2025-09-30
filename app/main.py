import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.api import agents
from app.data.entities.models import AgentInDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db = os.getenv("MONGODB_DB", "appdb")

    client = AsyncIOMotorClient(mongodb_uri)
    db = client[mongodb_db]

    await init_beanie(database=db, document_models=[AgentInDB])
    
    yield
    
    client.close()

def create_app() -> FastAPI:
    fastapi_app = FastAPI(title="Research Agent API", version="1.0", lifespan=lifespan)
    fastapi_app.include_router(agents.router)
    return fastapi_app

app = create_app()
