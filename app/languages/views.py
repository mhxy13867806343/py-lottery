from fastapi import APIRouter, Request,Depends,status
from sqlalchemy.orm import Session

from tool.classDb import httpStatus
from tool.db import getDbSession
from models.languages.operation import getListAll  # 假设 getListAll 函数能从数据库中获取节假日信息
from tool.dbLimit import minute110
from tool.dbThrottling import limiter
from pydantic import BaseModel

languagesApp = APIRouter()
@languagesApp.get("/search",description="获取语言辅助管理列表",summary="获取语言辅助管理列表")
def getLanguages(q:str="",db: Session = Depends(getDbSession)):
    # 假设 getListAll 函数接收一个年份参数，返回该年份的节假日信息列表
   return httpStatus(data=getListAll(db=db,q=q), message="获取成功", code=status.HTTP_200_OK)