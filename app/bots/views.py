from fastapi import APIRouter,Depends,status,Query,status
import requests

from tool.classDb import httpStatus
from tool.dbHeaders import outerUserAgentHeadersX64

botApp = APIRouter()

@botApp.get('/hot', description="热门列表", summary="热门列表")
def getHotList(show_type:str="",item_type:int=51,aid:str="2608",uuid:str="7352035066346472972",spider:int=0):
    url="https://api.juejin.cn/tag_api/v1/query_category_briefs"
    data={
        "show_type":show_type,
        "item_type":item_type,
        "aid":aid,
        "uuid":uuid,
        "spider":spider
    }
    result = requests.get(url, headers=outerUserAgentHeadersX64, params=data)
    return botJson(result)

@botApp.get('/home_theme_featured', description="", summary="")
def postHomeThemeFeatured(aid:int=2608,uuid:int=7352035066346472972,spider:int=0):
    url="https://api.juejin.cn/recommend_api/v1/bot/home_theme_featured"
    data={
        "aid": aid,
        "uuid": uuid,
        "spider": spider,
        "limit":10
    }
    result = requests.post(url, headers=outerUserAgentHeadersX64, data=data)
    return botJson(result)

@botApp.get('/recommend_all_feed', description="", summary="")
def postHomeRecommendAllFeed(aid:int=2608,uuid:int=7352035066346472972,spider:int=0,

id_type:int=51,sort_type:int=0,cursor:str="0",limit:int=12,channel_id:int=0,client_type:int=2608
                             ):
    url="https://api.juejin.cn/recommend_api/v1/bot/recommend_all_feed"
    params={
        "aid": aid,
        "uuid": uuid,
        "spider": spider,
    }
    data={
        "id_type": id_type,
        "sort_type": sort_type,
        "cursor": cursor,
        "limit": limit,
        "channel_id": channel_id,
        "client_type": client_type
    }
    result = requests.post(url, headers=outerUserAgentHeadersX64, data=data,params=params)
    return botJson(result)


def botJson(result):

    if result.status_code == 200:
        j = result.json()
        print(j,444444)
        if j.get("err_no") == 0:
            return httpStatus(code=status.HTTP_200_OK, message=j.get("err_msg"), data=j.get("data"))
        return httpStatus(code=status.HTTP_200_OK, message=j.get("err_msg"), data={})
    return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="获取失败", data={})