from fastapi import FastAPI,Request,status,APIRouter
from extend.db import LOCSESSION,Base,ENGIN # for database
from tool.appMount import staticMount
from tool.appAddMiddleware import appAddMiddleware
import uvicorn
from app.users.views import userApp as userRouterApi
from app.dynamic.views import dyApp as dyRouterApi
from app.signature.views import signatureApp as signatureRouterApi
from app.auxiliary.views import emailApp as emailAppRouterApi
router = APIRouter(
    prefix="/v1",  # 为这个路由器下的所有路由添加路径前缀 /v1
    tags=["v1"],  # 可选，为这组路由添加标签
)
app = FastAPI()
# 将 router 添加到 app 中
app.include_router(userRouterApi)
app.include_router(dyRouterApi)
app.include_router(signatureRouterApi)
app.include_router(emailAppRouterApi)
# CORS
appAddMiddleware(app)
# 静态文件
staticMount(app)

Base.metadata.create_all(bind=ENGIN)

app.include_router(router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    # uvicorn main.app --reload
    # uvicorn.run(app,host="localhost", port=8000)