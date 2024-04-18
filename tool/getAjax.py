import requests
import json
from datetime import datetime

from fastapi import status


def getHeadersHolidayUrl(year:int=datetime.now().year):
    url=f"https://timor.tech/api/holiday/year/{year}"
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    }
    holidayApi=requests.get(url,headers=headers).content
    api=json.loads(holidayApi)

    if api['code']==-1:
        return {
            "code":status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message":"服务出错",
        }
    if api['code']==0:
        if len(api['holiday']) == 0:
            return {
                "code": -80000,
                "message": "暂无数据",
            }
        return {
            "code": status.HTTP_200_OK,
            "message": "获取成功",
            "result": api['holiday'],
        }