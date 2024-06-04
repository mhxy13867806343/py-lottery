import time
from fastapi import FastAPI, APIRouter,Request,status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from extend.db import Base, ENGIN # 导入数据库相关模块
from tool.appMount import staticMount
from tool.appRate import appLimitRate
from tool.appAddMiddleware import appAddMiddleware
from sqlalchemy.exc import SQLAlchemyError

import uvicorn
from app.auxiliary.views import emailApp as emailAppRouterApi
from app.other.views import outerApp as outerAppRouterApi
from app.languages.views import languagesApp as languagesAppRouterApi
from app.users.views import userApp as userAppRouterApi
from tool.classDb import httpStatus
from tool.getLogger import globalLogger

# 创建主应用
app = FastAPI()

# 创建带全局前缀的路由器
v1_router = APIRouter(prefix="/v1")

# 将各个模块的路由添加到带前缀的路由器
v1_router.include_router(userAppRouterApi, prefix="/h5/user", tags=["用户管理"])
v1_router.include_router(emailAppRouterApi, prefix="/h5/email", tags=["邮件服务"])
v1_router.include_router(outerAppRouterApi, prefix="/h5/outer", tags=["辅助管理"])
v1_router.include_router(languagesAppRouterApi, prefix="/h5/languages", tags=["语言管理"])


# 将带有前缀的路由器添加到主应用
app.include_router(v1_router)
@app.get('/v1/ai')
async def test(name:str):
    import requests
    resource=requests.get(f"http://localhost:9910/hello/{name}")
    return httpStatus(data=resource.json(), message="获取成功", code=status.HTTP_200_OK)
@app.get('/v1/authorinfo',description="获取用户信息",summary="获取用户信息")
async def getIndexauthorUser():
    aiTool:dict={
        "aiTool": {
            "code": {
                "content": "AI代码助手",
                "list": [
                    {
                        "url": "https://github.com/features/copilot",
                        "type": "收费",
                        "language": "英文",
                        "id": "copilot"
                    },
                    {
                        "url": "https://codegeex.cn/zh-CN",
                        "type": "免费",
                        "language": "中文",
                        "id": "codegeex"
                    },
                    {
                        "url": "https://tongyi.aliyun.com/lingma/?channel=yy_AiBot&utm_content=m_1000388530",
                        "type": "免费",
                        "language": "中文",
                        "id": "lingma"
                    },
                    {
                        "url": "https://aws.amazon.com/cn/codewhisperer/",
                        "type": "免费或者收费",
                        "language": "英文或者中文",
                        "id": "codewhisperer"
                    },
                    {
                        "url": "https://codeium.com/",
                        "type": "免费",
                        "language": "英文",
                        "id": "codeium"
                    },
                    {
                        "url": "https://www.codium.ai/",
                        "type": "免费",
                        "language": "英文",
                        "id": "codium"
                    },
                    {
                        "url": "https://code.fittentech.com/",
                        "type": "免费",
                        "language": "英文或者中文",
                        "id": "fittentech"
                    },
                    {
                        "url": "https://comate.baidu.com/zh",
                        "type": "免费或者收费",
                        "language": "中文",
                        "id": "baidu"
                    }
                ]
            },
            "chat": {
                "content": "AI聊天助手",
                "list": [
                    {
                        "url": "https://www.bing.com/chat?q=Bing+AI&FORM=hpcodx",
                        "content": "微软的日常AI助手，提供聊天等服务。",
                        "id": "bing"
                    },
                    {
                        "url": "https://chat.openai.com/",
                        "content": "OpenAI提供的聊天式AI服务。",
                        "id": "openai_chat"
                    },
                    {
                        "url": "https://claude.ai/",
                        "content": "提供AI相关服务。",
                        "id": "claude"
                    },
                    {
                        "url": "https://gemini.google.com/app",
                        "content": "谷歌的AI平台。",
                        "id": "google_gp"
                    },
                    {
                        "url": "https://kimi.moonshot.cn/",
                        "content": "Kimi是一个具有超大'内存'的智能助手，可读完二十万字的小说，上网冲浪。",
                        "id": "kimi"
                    },
                    {
                        "url": "https://hunyuan.tencent.com/bot/chat",
                        "content": "腾讯的混元助手。",
                        "id": "tencent_hunyuan"
                    },
                    {
                        "url": "https://xinghuo.xfyun.cn/",
                        "content": "讯飞星火认知大模型，提供AI大语言模型服务。",
                        "id": "xfyun_xinghuo"
                    },
                    {
                        "url": "https://yiyan.baidu.com/?utm_source=ai-bot.cn",
                        "content": "百度提供的AI服务。",
                        "id": "baidu_yiyan"
                    },
                    {
                        "url": "https://chat.baidu.com/",
                        "content": "百度的文心一言，AI对话服务。",
                        "id": "baidu_wenxin"
                    },
                    {
                        "url": "https://secr.baidu.com/",
                        "content": "百度限app端使用的搜索服务。",
                        "id": "baidu_secr"
                    },
                    {
                        "url": "https://www.doubao.com/chat/",
                        "content": "豆包AI聊天助手，提供聊天、写作、翻译和编程等全能工具。",
                        "id": "doubao"
                    },
                    {
                        "url": "https://work.tiangong.cn/home/writting/",
                        "content": "天工AI助手，使用双千亿级大语言模型。",
                        "id": "tiangong"
                    },
                    {
                        "url": "https://chatglm.cn/?fr=mkazb01",
                        "content": "ChatGLM，智谱大模型，中国版ChatGPT。",
                        "id": "chatglm"
                    },
                    {
                        "url": "https://tongyi.aliyun.com/qianwen/",
                        "content": "通义千问，阿里巴巴的大语言模型。",
                        "id": "tongyi_qianwen"
                    },
                    {
                        "url": "https://www.baichuan-ai.com/chat",
                        "content": "百川智能，提供AI底座服务，优化意图理解和信息检索。",
                        "id": "baichuan"
                    },
                    {
                        "url": "https://www.coze.cn/",
                        "content": "扣子，创建专属于你的AI Bot。",
                        "id": "coze"
                    }
                ]

            }
        },
    }
    data={
        "version": "1.0.0",
        "authorName": "hooks",
        "authorEmail": "869710179@qq.com",
        "authorqq": "869710179",
        "createTime": int(time.time()),
        "authorWxid": "aigchooks",
        "authorImg": "static/wx/WechatIMG914.jpg",
        "githubHome": "https://github.com/mhxy13867806343?tab=repositories",
        "juejinHome": "https://juejin.cn/user/1310273588955581",
        "saying": "零的起点，从这里开始",
        **aiTool,
        "loveLanguage": [
            {
                "url": "https://www.python.org/",
                "name": "Python",

            },
            {
                "url": "https://www.rust-lang.org/",
                "name": "Rust",
            },
            {
                "url": "https://www.javascript.com/",
                "name": "JavaScript",
            },
            {
                "url": "https://www.typescriptlang.org/",
                "name": "TypeScript",
            }
        ],
        "industry": "前端开发，使用vue.js/uniapp/小程序/css/js/html/es6+",
        "site": [
            {
                "url": "https://www.github.com/",
                "name": "github"
            },
            {
                "url": "https://gitee.com",
                "name": "码云"
            },
            {
                "url": "https://juejin.cn/",
                "name": "掘金"
            },
            {
                "url": "https://www.cnblogs.com/",
                "name": "博客园"
            },
            {
                "url": "https://www.zhihu.com/",
                "name": "知乎"
            }
        ]
    }
    return httpStatus(data=data, message="获取成功", code=status.HTTP_200_OK)
# 中间件和其他配置
class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response: Response = await call_next(request)
            response.headers['X-Frame-Options'] = 'ALLOW-FROM https://example.com/'
            response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://example.com/"
            return response
        except SQLAlchemyError as e:
            globalLogger.exception("数据库操作出现异常:",e)
            return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="数据库操作出现异常")
        except Exception as e:
            globalLogger.exception("请求处理出现异常:",e)
            return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="请求处理出现异常")
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
