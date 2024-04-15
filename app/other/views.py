from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter,status
from tool.classDb import httpStatus
from tool.getAjax import getHeadersHolidayUrl
outerApp = APIRouter(
    prefix="/h5/outer",
    tags=["其他管理"]
)
@outerApp.get("/holiday")
async def getHoliday(year:int='')->List[dict]:
    """
    获取节假日信息
    :param year:
    :param month:
    :param day:
    :return:
    """

    return getHeadersHolidayUrl(year=year)