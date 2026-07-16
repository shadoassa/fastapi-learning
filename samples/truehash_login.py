from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt  #JSON Web Token
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "53aa26ff623a4f40afa38a3baf21ed309de68b309346b980610e174879816cbc" # ハッシュキー
ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

#パスワードのハッシュ化と検証に使うPasswordHashインスタンス
password_hash = PasswordHash.recommended()

# ダミー用ハッシュパスワード
DUMMY_HASH = password_hash.hash("dummypassword")

#リクエストヘッダーからトークンを自動で取得, tokenに格納
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# パスワード認証関数
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

# パスワードハッシュ化関数
def get_password_hash(password):
    return password_hash.hash(password)

# DB内のusernameに合致するユーザデータをUserクラスで返す関数
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

# ユーザとパスワードを検証, 合致すればuserクラスを返し, そうでなければFalseを返す
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user: #ユーザがDBにない場合
        verify_password(password, DUMMY_HASH)   #ダミーハッシュでの検証処理を挟むことによって, 応答時間による差異を出さない
        return False
    if not verify_password(password, user.hashed_password): #パスワードを検証
        return False
    return user

#dictで受け取り, トークンの有効期限を追加してjwtのアクセストークンを作成
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) #トークンをエンコード
    return encoded_jwt

#トークン
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #トークンをデコード
        username = payload.get("sub")   #"sub"にユーザの識別情報が入っている. そういう規定
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password) #リクエストフォームの情報をもとにDBからユーザを取得
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token( #認証に成功したらアクセストークンを作成
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]