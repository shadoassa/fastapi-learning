from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Todo(BaseModel):
    id: int
    title: str
    done: bool = False


class TodoCreate(BaseModel):
    title: str


todos_db: list[Todo] = []
_next_id = 1


def reset_todos() -> None:
    """テスト用: インメモリのTodoストアと採番カウンタを初期状態に戻す"""
    global _next_id
    todos_db.clear()
    _next_id = 1


@app.get("/hello")
async def hello() -> dict[str, str]:
    return {"message": "hello world!"}


@app.get("/todos")
async def list_todos() -> list[Todo]:
    return todos_db


@app.post("/todos", status_code=201)
async def create_todo(payload: TodoCreate) -> Todo:
    global _next_id
    todo = Todo(id=_next_id, title=payload.title, done=False)
    _next_id += 1
    todos_db.append(todo)
    return todo
