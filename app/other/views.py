import json
from typing import Optional, List
from datetime import datetime
import requests
import httpx
from fastapi import APIRouter,status,Request
from tool.classDb import httpStatus
from tool.getAjax import getHeadersHolidayUrl
from .model import OtherInput
from tool.dbLimit import minute110
from tool.dbThrottling import limiter
outerApp = APIRouter(
    prefix="/h5/outer",
    tags=["其他管理"]
)
@outerApp.get("/holiday")
@limiter.limit(minute110)
async def getHoliday(request: Request,year:int=''):
    """
    获取节假日信息
    :param year:
    :param month:
    :param day:
    :return:
    """
    return getHeadersHolidayUrl(year=year)
@outerApp.get("/searchgithub/{query}",description="搜索GitHub仓库名称",summary="搜索GitHub仓库名称")
async def test(query:Optional[str]='')->dict:
    if not query or len(query)==0:
        return httpStatus(data=query,message="请输入搜索内容")
    qg = """
    query SearchInputTipQuery($query: String!) {
      tips: searchTips(query: $query) {
        fullName
        sourceUrl
        url
        description
      }
    }
    """
    variables = {"query": query}
    qurl='https://www.github-zh.com/api/graphql'
    # 发送POST请求到GraphQL API端点
    response = requests.post(
        url=qurl,
        json={'query': qg, 'variables': variables},
        headers={'Content-Type': 'application/json'}
    )

    # 检查响应
    if response.ok:
        data = response.json()
        tips_data = data.get('data', {}).get('tips', [])
        tips_count = len(tips_data)  # 计算tips的长度
        if tips_count < 1:
            return httpStatus(data={}, message="暂无数据", code=status.HTTP_200_OK)

        # 在响应中添加tips的长度
        return httpStatus(data={"count": tips_count, "tips": tips_data}, message="获取成功",
                          code=status.HTTP_200_OK)

    else:
        # 如果GraphQL请求未能成功，则抛出异常
        raise httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="请求失败")

@outerApp.get("/iplocation",description="获取IP地址信息",summary="获取IP地址信息")
async def getWeather(ip:str="")->dict:
   url=f"https://webapi-pc.meitu.com/common/ip_location?ip={ip}"
   headers={
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

   }
   res=httpx.get(url,headers=headers)
   return httpStatus(data=res.json(),message="获取成功",code=status.HTTP_200_OK)
@outerApp.get("/weather",description="获取天气信息",summary="获取天气信息")
async def getWeather(location:str="")->dict:
    if not location or len(location)==0:
        return httpStatus(data={},message="请输入搜索或者选择城市")
    url=f"https://api.seniverse.com/v3/weather/now.json?key=e9znqfty5brmjfqj&location={location}&language=zh-Hans&unit=c"
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    res=requests.get(url,headers=headers)
    return httpStatus(data=res.json(),message="获取成功",code=status.HTTP_200_OK)
@outerApp.get("/city",description="获取城市信息",summary="获取城市信息")
async def cityJson()->dict:
    with open("static/files/city_json.json", "r", encoding="utf-8") as f:
        try:
            with open("static/files/city_json.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            return httpStatus(data=data.get("city"), message="获取成功", code=status.HTTP_200_OK)
        except json.JSONDecodeError:
            # JSON格式错误
            return httpStatus(data={}, message="JSON数据格式错误", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except FileNotFoundError:
            # 文件不存在
            return httpStatus(data={}, message="文件未找到", code=status.HTTP_404_NOT_FOUND)
        except PermissionError:
            # 文件权限问题
            return httpStatus(data={}, message="文件读取权限错误", code=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # 其他所有异常
            return httpStatus(data={}, message=f"未知错误: {str(e)}", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return httpStatus(data=data.get("city"),message="获取成功",code=status.HTTP_200_OK)
@outerApp.get("/hotcity",description="获取热门城市信息",summary="获取热门城市信息")
async def hotCity(number:int=12)->dict:
    url=f"https://geoapi.qweather.com/v2/city/top?number={number}&range=cn&key=85e5417c5f5a44b2b02ab27b5ba8be98"
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    res=requests.get(url,headers=headers)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
