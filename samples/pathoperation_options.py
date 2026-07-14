from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Enum classでタグを定義し, コードの可読性と保守性を向上
class Tags(Enum):
    items = "items"
    users = "users"

# Body用のItemモデルを定義
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()

# デコレータ関数にタグを追加することで, OpenAPIドキュメントでのグループ化が可能
@app.get("/items/", tags=[Tags.items])  
async def get_items():
    return ["Portal gun", "Plumbus"]


@app.get("/users/", tags=[Tags.users])
async def read_users():
    return ["Rick", "Morty"]

# deprecated=Trueを指定することで, OpenAPIドキュメント上で非推奨のエンドポイントとして表示される
@app.get("/elements/", tags=["items"], deprecated=True)
async def read_elements():
    return [{"item_id": "Foo"}]

@app.post(
    "/items/",
    tags=[Tags.items],
    summary="Create an item",   #summaryでエンドポイントの概要を追加
    # descriptionでエンドポイントの説明を追加可能
#    description="Create an item with all the information, name, description, price, tax and a set of unique tags",
    response_description="The created item" #response_descriptionでレスポンスの説明を追加
)
async def create_item(item: Item) -> Item:
    #docstringを使えば複数行に及ぶ詳細な説明を記述可能
    #Markdown形式で記述し, FastAPIは正しく解釈してOpenAPIドキュメントに反映
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item