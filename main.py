from typing import Union, Optional, List
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from models import ItemDocument


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


app = FastAPI(lifespan=lifespan)


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
    doc = ItemDocument(**item.model_dump())
    await doc.insert()
    return item


@app.get("/items", response_model=List[Item])
async def list_items() -> List[Item]:
    docs = await ItemDocument.find_all().to_list()
    return [Item(name=d.name, price=d.price, is_offer=d.is_offer) for d in docs]
