
from typing import Optional
import requests
from fastapi import APIRouter,status,Request
from tool.classDb import httpStatus
from tool.dbUrlResult import graphql
from tool.getAjax import getHeadersHolidayUrl
from tool.dbLimit import minute110
from tool.dbThrottling import limiter
from tool.dbHeaders import  jsHeaders

outerApp = APIRouter(
    prefix="/v1/h5/outer",
    tags=["其他管理"]
)
@outerApp.get("/holiday",description="输入年份获取节假日信息",summary="输入年份获取节假日信息")
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
@limiter.limit(minute110)
async def test(request: Request,query:Optional[str]='')->dict:
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
    # 发送POST请求到GraphQL API端点
    response = requests.post(
        url=graphql,
        json={'query': qg, 'variables': variables},
        headers=jsHeaders
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
