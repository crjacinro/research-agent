from typing import Optional

from beanie import Document


class ItemDocument(Document):
    name: str
    price: float
    is_offer: Optional[bool] = None

    class Settings:
        name = "items" 