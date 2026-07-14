from fastapi import FastAPI, HTTPException # ←fastAPIのHTTPExceptionはStarletteのHTTPExceptionを継承している
from fastapi.exception_handlers import ( # ←fastapiの例外ハンドラ
    http_exception_handler,
    request_validation_exception_handler,   
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException # ←RenameしてStarletteのHTTPExceptionをインポート
# この処理によって, FastAPIのHTTPExceptionとStarletteのHTTPExceptionを区別して使えるようになる  

app = FastAPI()

# StarletteのHTTPExceptionをキャッチする例外ハンドラ
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"OMG! An HTTP error!: {repr(exc)}")
# fastapiのデフォルトのhttp_exception_handlerを呼び出すことで, 既存の処理を再利用できる
    return await http_exception_handler(request, exc)

# プレーンテキストで返す場合は以下のようにする
# @app.exception_handler(StarletteHTTPException)
# async def custom_http_exception_handler(request, exc):
#   return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

# FastAPIのRequestValidationErrorをキャッチする例外ハンドラ
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}