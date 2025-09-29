from typing import Union, List
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.api import agents
from app.data.entities.models import ItemDocument


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db = os.getenv("MONGODB_DB", "appdb")

    client = AsyncIOMotorClient(mongodb_uri)
    db = client[mongodb_db]

    await init_beanie(database=db, document_models=[ItemDocument])
    
    yield
    
    client.close()

def create_app() -> FastAPI:
    fastapi_app = FastAPI(title="Research Agent API", version="1.0", lifespan=lifespan)
    fastapi_app.include_router(agents.router)
    return fastapi_app

app = create_app()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/ping")
def read_root():
    return "pong"

@app.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
    doc = ItemDocument(**item.model_dump())
    await doc.insert()
    return item


@app.get("/items", response_model=List[Item])
async def list_items() -> List[Item]:
    docs = await ItemDocument.find_all().to_list()
    return [Item(name=d.name, price=d.price, is_offer=d.is_offer) for d in docs]
