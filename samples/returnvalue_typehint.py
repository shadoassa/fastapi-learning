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