import requests
import json
from datetime import datetime

def getHeadersHolidayUrl(year:int=datetime.now().year,headers:dict={})->dict:
    url=f"https://timor.tech/api/holiday/year/{year}"
    holidayApi=requests.get(url,headers=headers).content
    api=json.loads(holidayApi)

    if api['code']==-1:
        return {
            "code":api['code'],
            "message":"服务出错",
        }
    if api['code']==0:
        if len(api['holiday']) == 0:
            return {
                "code": -2,
                "message": "暂无数据",
            }
        return {
            "code": api['code'],
            "message": "获取成功",
            "result": api['holiday'],
        }