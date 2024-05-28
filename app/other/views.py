
from typing import Optional
import requests
import json
from fastapi import APIRouter,status,Request
from tool.classDb import httpStatus
from tool.dbKey import hotCityKey
from tool.dbTools import generate_dynamic_cookies
from tool.dbUrlResult import graphql, qwCityUrl, locationWeatherUrl, aweatherapiytrsss7
from tool.getAjax import getHeadersHolidayUrl
from tool.dbLimit import minute110
from tool.dbThrottling import limiter
from tool.dbHeaders import jsHeaders, outerUserAgentHeadersX64

outerApp = APIRouter()

@outerApp.get("/ai/tool/category",description="ai分类",summary="ai分类")
async  def toolcategory():
    file_path="static/json/toolAi.json"
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        return httpStatus(data=data, code=status.HTTP_200_OK,message="获取成功")
    except FileNotFoundError:
        return httpStatus(message='未找到相关资源', status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return httpStatus(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
@outerApp.get('/toolaiAi')
async def toolaiAi(pageIndex:int=1,pageSize:int=12,key:str="test",
                   Category:str=""):
    cookies = generate_dynamic_cookies()
    if not Category or len(Category)==0:
        url=f"https://www.toolai.io/api/AI/GetIndexData?PageIndex={pageIndex}&PageSize={pageSize}&Key={key}"
    else:
        url=f"https://www.toolai.io/api/AI/GetDataByCategory?PageIndex={pageIndex}&PageSize={pageSize}&Key={key}&Category={Category}&Sort=id desc"
    outerUserAgentHeadersX64["X-Requested-With"]="XMLHttpRequest"

    result = requests.get(url, headers=outerUserAgentHeadersX64,cookies=cookies)
    if result.status_code != 200:
        return httpStatus(code=result.status_code, message="未找到相关资源")
    return httpStatus(data=result.json(), message="获取成功", code=status.HTTP_200_OK)
@outerApp.get('/design',description="获取图片信息",summary="获取图片信息")
async def getDesign(type:str="dribbble",limit:int=20,offset:int=0):
    url = f"https://e.juejin.cn/resources/{type}"
    data={
        "limit": limit,
        "offset": offset
    }
    result = requests.post(url, headers=outerUserAgentHeadersX64,json=data)
    if result.status_code != 200:
        return httpStatus(code=result.status_code, message="未找到相关资源")
    return httpStatus(data=result.json().get("data"), message="获取成功", code=status.HTTP_200_OK)
@outerApp.get('/hotApi',description="获取热搜榜信息",summary="获取热搜榜信息")
async def getHot(type:str="baiduhot"):
    url = f"https://tenapi.cn/v2/{type}"

    result = requests.post(url, headers=outerUserAgentHeadersX64)
    if result.status_code != 200:
        return httpStatus(code=result.status_code, message="未找到相关资源")
    return httpStatus(data=result.json().get("data"), message="获取成功", code=status.HTTP_200_OK)

@outerApp.get('/ithome',description="获取it之家信息",summary="获取it之家信息")
async def ithome(limit:int=20,offset:int=0):
    url = "https://e.juejin.cn/resources/ithome"
    data={
        "limit": limit,
        "offset": offset
    }
    result = requests.post(url, headers=outerUserAgentHeadersX64,json=data)
    if result.status_code != 200:
        return httpStatus(code=result.status_code, message="it之家请求失败")
    return httpStatus(data=result.json().get("data"), message="获取成功", code=status.HTTP_200_OK)
@outerApp.get('/v2ex',description="获取v2ex信息",summary="获取v2ex信息")
async def v2ex(limit:int=20,offset:int=0):
    url = "https://e.juejin.cn/resources/v2ex"
    data={
        "limit": limit,
        "offset": offset
    }
    result = requests.post(url, headers=outerUserAgentHeadersX64,json=data)
    if result.status_code != 200:
        return httpStatus(code=result.status_code, message="V2EX请求失败")
    return httpStatus(data=result.json().get("data"), message="获取成功", code=status.HTTP_200_OK)
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
@outerApp.get('/search/q')
async def githubSearch(q:str="",p:int=1,type:str="repositories"):
    try:
        url = f"https://github.com/search?q={q}&type={type}&p={p}"
        result = requests.get(url, headers=outerUserAgentHeadersX64)
        if result.status_code != 200:
            raise httpStatus(code=result.status_code, message="GitHub请求失败")
        js = result.json()
        if js.get('payload').get("type") == 'home':
            return httpStatus(data=[], message="暂无数据", code=status.HTTP_200_OK)
        return httpStatus(data=js.get("payload"), message="获取成功", code=status.HTTP_200_OK)
    except requests.RequestException as e:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST, message="GitHub请求失败")
    except Exception as e:
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="处理响应时出现错误")

@outerApp.get('/search/github')
async def github1Search(period:str="day",offset:int=0,lang:str="python",category:str="trending",
limit:int=50
                        ):
    try:
        data={
    "category":category,
    "period":period,
    "lang": lang,
    "offset": offset,
    "limit":limit
}
        url = f"https://e.juejin.cn/resources/github"
        result = requests.post(url,json=data, headers=outerUserAgentHeadersX64)
        if result.status_code != 200:
            raise httpStatus(code=result.status_code, message="GitHub请求失败")
        return httpStatus(data=result.json().get("data"), message="获取成功", code=status.HTTP_200_OK)
    except requests.RequestException as e:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST, message="GitHub请求失败")
    except Exception as e:
        print(e,555555555)
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="处理响应时出现错误")

@outerApp.get("/searchgithub/{query}",description="搜索GitHub仓库名称",summary="搜索GitHub仓库名称")
@limiter.limit(minute110)
async def test(request: Request,query:str="")->dict:
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
@outerApp.get("/weather",description="获取天气信息",summary="获取天气信息")
@limiter.limit(minute110)
async def getWeather(request: Request,location:str="")->dict:
    if not location or len(location)==0:
        return httpStatus(data={},message="请输入搜索或者选择城市")
    url=f"{locationWeatherUrl}&location={location}&language=zh-Hans&unit=c"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    return httpStatus(data=res.json(),message="获取成功",code=status.HTTP_200_OK)
@outerApp.get("/city",description="获取城市信息",summary="获取城市信息")
@limiter.limit(minute110)
async def cityJson(request: Request,)->dict:
    city="static/files/city_json.json"
    try:
        with open(city, "r", encoding="utf-8") as f:
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
@outerApp.get("/hotcity",description="获取热门城市信息",summary="获取热门城市信息")
@limiter.limit(minute110)
async def hotCity(request: Request,number:int=12)->dict:
    url=f"{qwCityUrl}?number={number}&range=cn&key={hotCityKey}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
@outerApp.get("/cityname",description="未来十五日天气",summary="未来十五日天气")
@limiter.limit(minute110)
async def cityname(request: Request,cityname:str="")->dict:
    if not cityname or len(cityname)==0:
        return httpStatus(data={},message="请输入或者选择城市名")
    url=f"{aweatherapiytrsss7}?cityname={cityname}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        if res.text=="未能解析城市代码！":
            return httpStatus(data={}, message="未能获取到该城市的天气信息", code=status.HTTP_400_BAD_REQUEST)
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)