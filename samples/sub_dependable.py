#---------------
# 深くネストされた依存関係を使用する例
# 今後, securityについての章で有用性が示される.
#---------------

from typing import Annotated
from fastapi import Cookie, Depends, FastAPI

app = FastAPI()


# 最初の依存関数
def query_extractor(q: str | None = None):
    return q

# 2つ目の依存関数
def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    if not q:
        return last_query
    return q


@app.get("/items/")
async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor)], #依存関係の使用
):
    return {"q_or_cookie": query_or_default}