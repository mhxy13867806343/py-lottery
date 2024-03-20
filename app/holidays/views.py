from fastapi import APIRouter,Depends,status,Request
from tool.getAjax import getHeadersHolidayUrl
holidaysApp = APIRouter(
    prefix="/h5/festival",
    tags=["用户管理"]
)
@holidaysApp.get("/info",description="获取节假日信息",summary="获取节假日信息")
async def root(request: Request)->dict:
    user_agent = request.headers.get('User-Agent')
    headers={"User-Agent": user_agent}
    return {
        "data":{
            "message": "获取成功",
            "result": {
                **getHeadersHolidayUrl(headers=headers),
                "UserAgent": user_agent,

            }
        }
    }