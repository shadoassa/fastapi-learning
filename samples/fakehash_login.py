from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# 仮のDB
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()

#　仮のパスワードハッシュ関数
def fake_hash_password(password: str):
    return "fakehashed" + password

#リクエストヘッダーを自動的にvalidationし, トークンを取り出してtokenに格納する処理
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

# ハッシュパスワード情報付きのUserクラス
class UserInDB(User):
    hashed_password: str

# usernameがDBにあるなら, そのusernameに該当するハッシュパスワード情報付きのUserクラスを返す.
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

#tokenから, 現在ログイン中のユーザ情報を返す関数
def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

# リクエストヘッダーのtokenから, 現在ログイン中のユーザ情報を返す関数
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# get_current_active_userに依存し, 取得したユーザが現在利用可能かを判定する関数
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

#/tokenパスへのPOSTに対するログイン処理
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)   #リクエストフォームデータのユーザネームを参照し, データベースからユーザ情報を取得
    if not user_dict:   # データベースになければエラー
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)    # ハッシュパスワード情報入りのUserクラスを取得
    hashed_password = fake_hash_password(form_data.password)    #リクエストフォームデータのパスワードを参照してハッシュ化
    if not hashed_password == user.hashed_password: # 登録情報と入力情報のパスワードが違ったらエラー
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}  # 合致したらJSON形式でレスポンス

# 現在ログイン中のユーザ情報を取得
@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user