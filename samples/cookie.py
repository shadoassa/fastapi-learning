from typing import Annotated
from fastapi import Cookie, FastAPI
from pydantic import BaseModel

app = FastAPI()

# Cookieパラメータモデル
class Cookies(BaseModel):
    model_config = {"extra": "forbid"}  # 余計なフィールドがある場合はエラーにする処置

    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies