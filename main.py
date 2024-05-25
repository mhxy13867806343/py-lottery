from fastapi import FastAPI, APIRouter,Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from extend.db import Base, ENGIN # 导入数据库相关模块
from tool.appMount import staticMount
from tool.appRate import appLimitRate
from tool.appAddMiddleware import appAddMiddleware
import uvicorn
from app.auxiliary.views import emailApp as emailAppRouterApi
from app.other.views import outerApp as outerAppRouterApi
from app.languages.views import languagesApp as languagesAppRouterApi
from app.users.views import userApp as userAppRouterApi
from app.dynamic.views import dyApp as dyAppRouterApi

# 创建主应用
app = FastAPI()

# 创建带全局前缀的路由器
v1_router = APIRouter(prefix="/v1")

# 将各个模块的路由添加到带前缀的路由器
v1_router.include_router(userAppRouterApi, prefix="/h5/user", tags=["用户管理"])
v1_router.include_router(dyAppRouterApi, prefix="/h5/dynamic", tags=["用户动态管理"])
v1_router.include_router(emailAppRouterApi, prefix="/h5/email", tags=["邮件服务"])
v1_router.include_router(outerAppRouterApi, prefix="/h5/outer", tags=["辅助管理"])
v1_router.include_router(languagesAppRouterApi, prefix="/h5/languages", tags=["语言管理"])

# 将带有前缀的路由器添加到主应用
app.include_router(v1_router)

# 中间件和其他配置
class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers['X-Frame-Options'] = 'ALLOW-FROM https://example.com/'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://example.com/"
        return response

# 添加CORS和自定义中间件
appAddMiddleware(app)
app.add_middleware(CustomHeaderMiddleware)

# 静态文件和限流
staticMount(app)
appLimitRate(app)

# 初始化数据库
Base.metadata.create_all(bind=ENGIN)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
