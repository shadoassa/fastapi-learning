from typing import Annotated, Literal
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

# クエリパラメータモデル (BaseModelで作成)
class FilterParams(BaseModel):
    #余分なクエリパラメータを受け取るとエラーにする設定
    model_config = {"extra": "forbid"} 

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query