from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder # pydanticのモデルを受け取り, JSON互換版を返す
from pydantic import BaseModel

fake_db = {}


class Item(BaseModel):
    title: str
    timestamp: datetime #fake_dbにdatetime型は非対応
    description: str | None = None


app = FastAPI()


@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)  #item内のdatetimeをstr型に変換
    fake_db[id] = json_compatible_item_data