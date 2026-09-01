from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Todo(BaseModel):
    id: int
    title: str
    done: bool = False


class TodoCreate(BaseModel):
    title: str


class TodoUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


todos_db: list[Todo] = []
_next_id = 1


def reset_todos() -> None:
    """テスト用: インメモリのTodoストアと採番カウンタを初期状態に戻す"""
    global _next_id
    todos_db.clear()
    _next_id = 1


def _find_todo(todo_id: int) -> Todo:
    for todo in todos_db:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")


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


@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int) -> Todo:
    return _find_todo(todo_id)


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, payload: TodoUpdate) -> Todo:
    todo = _find_todo(todo_id)
    if payload.title is not None:
        todo.title = payload.title
    if payload.done is not None:
        todo.done = payload.done
    return todo


@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: int) -> None:
    todo = _find_todo(todo_id)
    todos_db.remove(todo)
