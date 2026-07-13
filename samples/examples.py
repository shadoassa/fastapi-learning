from typing import Annotated
from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Annotated[Item, Body(
            examples=[ # ←examplesとして実際に使える例を定義する.　これらはValidationには影響を与えない.
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
                {  # ←複数の例を定義することも可能.
                    "name": "Bar",
                    "price": "35.4",
                },
                {  # ←不正な例を定義することも可能.
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results