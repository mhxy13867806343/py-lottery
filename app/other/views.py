import json
from typing import Optional, List
from datetime import datetime
import requests
import httpx
from fastapi import APIRouter,status,Request
from tool.classDb import httpStatus
from tool.dbKey import hotCityKey, youjiaKey
from tool.dbUrlResult import graphql, ipLocationUrl, locationWeatherUrl, qwCityUrl, efefeeeUrlHot, vvhanApiUrl, \
    movieOnInfoListUrl, duanjuapiSearchPhp, QQyyscUrl, aweatherapiytrsss7, api777camjson, zzxjjvideosUrl, apigirlUrl, \
    mteladresscommon, dmlisturl, pictureUrl, wordscanUrl, wordcloudUrl, dysearchUrl, \
    kfc4Url, lunarUrl, baikeUrl, rubbishUrl, deliveryUrl, youjiaUrl
from tool.vhot import  hotListType
from tool.getAjax import getHeadersHolidayUrl
from .model import OtherInput
from tool.dbLimit import minute110
from tool.dbThrottling import limiter
from tool.dbHeaders import outerUserAgentHeadersX64, jsHeaders

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
@outerApp.post("/youjia",description="今日国内油价查询",summary="今日国内油价查询")
@limiter.limit(minute110)
async def getYoujiaUrl(request: Request)->dict:
    url=f"{youjiaUrl}?key={youjiaKey}"
    res=httpx.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        if res.json().get("code")==1:
            return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
@outerApp.get("/iplocation",description="获取IP地址信息",summary="获取IP地址信息")
@limiter.limit(minute110)
async def getWeather(request: Request,ip:str="")->dict:
   url=f"{ipLocationUrl}?ip={ip}"
   res=httpx.get(url,headers=outerUserAgentHeadersX64)
   return httpStatus(data=res.json(),message="获取成功",code=status.HTTP_200_OK)
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
@outerApp.get("/hotlist",description="获取分类列表",summary="获取分类列表")
@limiter.limit(minute110)
async def getHotList(request: Request)->dict:
    return httpStatus(data=hotListType, message="获取成功", code=status.HTTP_200_OK)
@outerApp.get("/hotblog",description="获取热门博客信息",summary="获取热门博客信息")
@limiter.limit(minute110)
async def getVhotList(request: Request,type="")->dict:
    if not type:
        type=hotListType[0].get("name")
    url=f"{efefeeeUrlHot}{type}?cache=true"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get('/touchTheFish' ,description="摸鱼",summary="摸鱼")
@limiter.limit(minute110)
async def touchTheFish(request: Request, type: str = "moyu") -> dict:
   try:
       url = f"{vvhanApiUrl}{type}?type=json"
       async with httpx.AsyncClient() as client:
           res = await client.get(url, headers=outerUserAgentHeadersX64)
       if res.status_code == 200:
           result = res.json()
           if result.get("success"):
               if type == "wyMusic/原创榜":
                   a = {"url": result.get("info", {}).get("url")}
               elif type == "text/joke":
                   a = {"url": result.get("data", {}).get("content")}
               elif type == "moyu":
                   a = {"url": result.get("url")}
               else:
                   a = {"url": result.get("url")}  # 默认情况下使用通用 URL 结构

               return httpStatus(data=a, message="获取成功", code=status.HTTP_200_OK)
           return httpStatus(data={}, message="未获取到数据", code=status.HTTP_400_BAD_REQUEST)
       else:
           raise httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="服务器错误")
   except httpStatus as e:
        return httpStatus(data=e.data, message=e.message, code=e.code)
@outerApp.get("/hotlistall",description="集合列表",summary="集合列表")
@limiter.limit(minute110)
async def getHotListAll(request: Request)->dict:
    url=f"{vvhanApiUrl}hotlist/all"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        result= res.json()
        return httpStatus(data=result, message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
@outerApp.get("/movieOnInfoList",description="正在热门电影",summary="正在热门电影")
@limiter.limit(minute110)
async def movieOnInfoList(request: Request)->dict:
    res=requests.get(movieOnInfoListUrl,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        result= res.json()

        return httpStatus(data=result, message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get("/duanjuapi",description="短剧搜索",summary="短剧搜索")
@limiter.limit(minute110)
async def duanjuapi(request: Request,text:str="")->dict:
    if not text or len(text)==0:
        return httpStatus(data={},message="请输入搜索内容")
    url=f"{duanjuapiSearchPhp}?text={text}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        result= res.json()

        return httpStatus(data=result, message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get("/qQyysc",description="获取72小时左右的音乐时长",summary="获取72小时左右的音乐时长")
@limiter.limit(minute110)
async def qQyysc(request: Request,qq:str="")->dict:
    if not qq or len(qq)==0:
        return httpStatus(data={},message="请输入QQ号")
    url=f"{QQyyscUrl}?text={qq}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data={
            "qq":f"搜索的QQ号为{qq}",
            "text":res.text
        }, message="获取成功", code=status.HTTP_200_OK)
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

@outerApp.get("/douyinMM",description="抖音MM",summary="抖音MM")
@limiter.limit(minute110)
async def douyinMM(request: Request,)->dict:
    res=requests.get(api777camjson,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@outerApp.get("/zzxjj",description="快手MM",summary="快手MM")
@limiter.limit(minute110)
async def zzxjj(request: Request,)->dict:
    res=requests.get(zzxjjvideosUrl,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.url, message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@outerApp.get("/girlMM",description="girlMM",summary="girlMM")
@limiter.limit(minute110)
async def girlMM(request: Request,)->dict:
    res=requests.get(apigirlUrl,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@outerApp.get("/mobile",description="查询手机号归属地",summary="查询手机号归属地")
@limiter.limit(minute110)
async def getMobile(request: Request,mobile:str="")->dict:
    if not mobile or len(mobile)==0:
        return httpStatus(data={},message="请输入手机号")
    url=f"{mteladresscommon}?mobile={mobile}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get("/dmlishi",description="历史上的今天",summary="历史上的今天")
@limiter.limit(minute110)
async def getdmLishi(request: Request,dmLishi:str="")->dict:
    url=f"{dmlisturl}?date={dmLishi}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)






@outerApp.get("/picture",description="图片搜索",summary="图片搜索")
@limiter.limit(minute110)
async def getPicture(request: Request,page:int=1)->dict:
    url=f"{pictureUrl}?page={page}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get("/word",description="文本敏感词检测",summary="文本敏感词检测")
@limiter.limit(minute110)
async def getWord(request: Request,word:str="")->dict:
    if not word or len(word)==0:
        return httpStatus(data={},message="请输入文本敏感词检测内容")
    url=f"{wordscanUrl}?word={word}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        if res.json().get("verdict")=='malicious':
            return httpStatus(data={}, message=f"已存在敏感关键字{word}", code=status.HTTP_200_OK)
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@outerApp.get("/wordcloud",description="文本内容",summary="文本内容")
@limiter.limit(minute110)
async def getWordcloud(request: Request,word:str="")->dict:
    if not word or len(word)==0:
        return httpStatus(data={},message="请输入文本内容")
    url=f"{wordcloudUrl}?text={word}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get("/dysearch",description="抖音搜索",summary="抖音搜索")
@limiter.limit(minute110)
async def getdysearch(request: Request,keyword:str="",page:int=1)->dict:
    if not keyword or len(keyword)==0:
        return httpStatus(data={},message="请输入内容")
    url=f"{dysearchUrl}?keyword={keyword}&page={page}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get("/kfc",description="疯狂星期四",summary="疯狂星期四")
@limiter.limit(minute110)
async def getkfc(request: Request,)->dict:
    url=f"{kfc4Url}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get("/lunar",description="具有黄历、农历、节日、星期等信息，支持阴历/阳历反查",summary="具有黄历、农历、节日、星期等信息，支持阴历/阳历反查")
@limiter.limit(minute110)
async def getLunar(request: Request,data:str="")->dict:
    url=f"{lunarUrl}?data={data}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@outerApp.get("/baike",description="百科全书",summary="百科全书")
@limiter.limit(minute110)
async def getBaike(request: Request,msg:str="")->dict:
    if not msg or len(msg)==0:
        return httpStatus(data={},message="请输入内容")
    url=f"{baikeUrl}?msg={msg}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@outerApp.get("/rubbish",description="垃圾分类",summary="垃圾分类")
@limiter.limit(minute110)
async def getRubbish(request: Request,name:str="")->dict:
    if not name or len(name)==0:
        return httpStatus(data={},message="请输入内容")
    url=f"{rubbishUrl}?name={name}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@outerApp.get("/delivery",description="快递查询",summary="快递查询")
@limiter.limit(minute110)
async def getDelivery(request: Request,nu:str="")->dict:
    if not nu or len(nu)==0:
        return httpStatus(data={},message="请输入内容")
    url=f"{deliveryUrl}?nu={nu}"
    res=requests.get(url,headers=outerUserAgentHeadersX64)
    if res.status_code==200:
        return httpStatus(data=res.json(), message="获取成功", code=status.HTTP_200_OK)
    else:
        return httpStatus(data={}, message="获取失败", code=status.HTTP_500_INTERNAL_SERVER_ERROR)