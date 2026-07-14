from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

# ユーザの基本情報を表すモデル
class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

# BaseUserを継承して、パスワードを追加したモデル
class UserIn(BaseUser):
    password: str

# UserInを受け取り、BaseUserを返すようにすることで、パスワードは返却されないようにする.
@app.post("/user/")
async def create_user(user: UserIn) -> BaseUser: #FastAPIはこのValidationを自動で行う.
    return user

# ----- ----- -----

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get(""
    "/items/{item_id}",
    response_model=Item,    # 戻り値の型ヒントをresponse_modelで設定できる.
    response_model_exclude_unset=True #デフォルト値が設定されていない場合は、レスポンスに含めないようにする.
)
async def read_item(item_id: str):
    return items[item_id]

@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"}, # レスポンスに含めるフィールドを指定する
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get(
    "/items/{item_id}/public",
    response_model=Item,
    response_model_exclude={"tax"} # レスポンスから除外するフィールドを指定する
)
async def read_item_public_data(item_id: str):
    return items[item_id]