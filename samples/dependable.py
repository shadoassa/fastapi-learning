from typing import Annotated, Any
from fastapi import Depends, FastAPI

app = FastAPI()


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

#依存関係としての関数
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

#依存関係としてのクラス
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit
#こっちの方が, エディタのサポートなどを受け取れるので便利.


@app.get("/items/")
async def read_items(commons: Annotated[CommonQueryParams, Depends()]): # Depends()を使うことで、依存関係としてのクラスを指定できる.
#async def read_items(commons: Annotated[Any, Depends(CommonQueryParams)]): # ← これでも同じ意味になる. 
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response