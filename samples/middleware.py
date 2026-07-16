import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware  #Cross-Origin Resource Sharing の設定用

app = FastAPI()

origins = [ #接続を許可するOriginたち
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  #A: originsを許可
    allow_credentials=True, #B: Cookieなどを許可
    allow_methods=["*"],    #C: HTTPメソッドを許可
    allow_headers=["*"],    #D: ヘッダーを許可
)

#E: デコレータで実行時間をヘッダーに追加するミドルウェアを設定
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

#ミドルウェアは定義した順にラップされるので, この場合
#Request: E>D>C>B>A>route
#Response: route>A>B>C>D>E の順で実行される

@app.get("/")
async def main():
    return {"message": "Hello World"}
