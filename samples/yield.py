from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException

app = FastAPI()

data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}

class OwnerError(Exception):
    pass

class InternalError(Exception):
    pass

# yieldとHTTPExceptionを組み合わせて、依存関係の中で例外を処理する例
def get_username():
    try:
        yield "Rick"    # [2] ユーザ名 "Rick" を返し, yieldの位置で処理を一時停止
                        # [7] yieldの位置で再開, あたかもyield "Rick"の行でOwnerErrorが発生したという形で伝えられる
    except OwnerError as e: #[8] 例外を捕まえ, HTTPExceptionに変換して返す
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")
    except InternalError:   # exceptを持つ依存関係において,
        print("We don't swallow the internal error here, we raise again 😎")
        #↑ここまでだけだと, クライアントには適切にエラーが返るが, サーバにはログが一切残らない
        raise   #yieldとexceptを持つ場合, 必ず再raiseを行う. 
        #↑これによりFastAPIが例外を認識し, サーバにログが残る. raiseだけで同じ例外を再raiseできる.


@app.get("/items/{item_id}") #　[1]/items/plumbus にアクセスした場合、依存関係に従ってget_username() が呼び出される
def get_item(
    item_id: str,
    username: Annotated[str, Depends(get_username)] # [3] usernameに"Rick"が代入される
):
    if item_id not in data: #[4] 今回はdataに"plumbus"があるので、ここはスキップされる
        raise HTTPException(status_code=404, detail="Item not found")
    item = data[item_id]    #[5] itemにdata["plumbus"]が代入される
    if item["owner"] != username:   #[6] "Morty" != "Rick"がTrueとなるので、OwnerErrorが発生する
        raise OwnerError(username)  #　  ここでget_item()の処理が中断され、例外が投げられる
    return item

@app.get("/items/{item_id}/must_raise") #yieldとexceptを使った時の再raiseの使用例
def get_item_must_raise(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id == "portal-gun":
        raise InternalError(
            f"The portal gun is too dangerous to be owned by {username}"
        )   #ここでget_username()のexceptへ
    if item_id != "plumbus":
        raise HTTPException(
            status_code=404, detail="Item not found, there's only a plumbus here"
        )
    return item_id