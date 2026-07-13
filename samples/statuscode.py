from fastapi import FastAPI

app = FastAPI()

# レスポンスにステータスコードを設定可能
@app.post("/items/", status_code=201)
async def create_item(name: str):
    return {"name": name}