from typing import Optional, List

import requests
from fastapi import APIRouter, Depends, status, Query,Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta

from tool.dbKey import suapiKey
from tool.dbLimit import minute110
from tool.dbThrottling import limiter
from tool.dbUrlResult import badwordUrl, ipinfoProUrl
from .model import AuxiliaryInputFirst, AuxiliaryInputPostNunSize, AuxiliaryCopyInput
from models.auxiliary.operation import getEmailList,getEmailTotal
from tool.db import getDbSession
from models.auxiliary.model import Email, CopyEmail
from tool.classDb import httpStatus, validate_email_str,validate_encrypt_email
from tool.statusTool import EXPIRE_TIME
from .tools import sendEmail,isSend,generateEmailId,sbError
from tool.takw import getArgsKwArgsResult
expires_delta = timedelta(minutes=EXPIRE_TIME)
emailApp = APIRouter()
@emailApp.get('/list',description="邮箱列表",summary="邮箱列表")
async def postEmailList(email:str = Query(''), pageNum: int = 1, pageSize: int =10, session: Session = Depends(getDbSession)):
    if not email:
        return httpStatus(message="邮箱不能为空", data={})
    try:
        res:[str or bool]=validate_encrypt_email(email)
        result={
            "total":getEmailTotal(email=email,session=session),
            "data":getEmailList(email=email,session=session,pageNum=pageNum,pageSize=pageSize),
            "pageNum":pageNum,
            "pageSize":pageSize,
        }
        result["searchEmail"]= res if result["total"] != 0 else res
        return getArgsKwArgsResult(**result)
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus()
@emailApp.post('/send',description="发送邮箱",summary="发送邮箱")
def postSendEmail(aed:AuxiliaryInputFirst,session:Session = Depends(getDbSession)):
    title:str=aed.title
    email:str=aed.email
    content:str=aed.content
    if not email:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="邮箱不能为空",data={})
    if not validate_email_str(email):
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="邮箱格式不正确",data={})
    if not content:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="内容不能为空",data={})
    try:
        if sbError:
            return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="发送失败",data={})
        if isSend:
            rTime = int(time.time())
            emailId = generateEmailId(email_address=email)
            sendEmail(title=title,content=content,from_email=email)
            resultSql = Email(email=email, title=title, content=content, create_time=rTime,
                              email_id=emailId,status=0
                              )
            session.add(resultSql)
            session.commit()
            return httpStatus(code=status.HTTP_200_OK,message="发送成功",data={})
        else:
            return httpStatus()
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus()
@emailApp.get('/copy/{id}',description="克隆邮箱列表",summary="克隆邮箱列表")
def getCopyEmailList(id:int,session:Session = Depends(getDbSession)):
    if not id:
        return httpStatus(message="id不能为空", data={})
    db_email = session.query(CopyEmail).filter(CopyEmail.email_id == id).all()
    db_count = session.query(CopyEmail).filter(CopyEmail.email_id == id).count()
    data={
        "data":db_email,
        "total":db_count
    }
    return httpStatus(data=data,code=status.HTTP_200_OK,message="获取成功")
@emailApp.post('/send/copy',description="克隆邮箱",summary="克隆邮箱")
def postSendEmailCopy(apns:AuxiliaryCopyInput,session:Session = Depends(getDbSession)):
    title:str=apns.title
    email:str=apns.email
    content:str=apns.content
    email_id=apns.email_id
    if not email_id:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="email_id不能为空",data={})
    if not email:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="邮箱不能为空",data={})
    if not validate_email_str(email):
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="邮箱格式不正确",data={})
    if not content:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="内容不能为空",data={})
    try:
        if isSend:
            rTime = int(time.time())
            sendEmail(title=title,content=content,from_email=email)
            resultSql = CopyEmail(email=email, title=title, content=content, create_time=rTime,
                                   email_id=email_id,status=0)
            session.add(resultSql)
            session.commit()
            return httpStatus(code=status.HTTP_200_OK,message="克隆成功",data={})
        else:
            return httpStatus()
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus()

@emailApp.get('/send/badword',description="敏感词库/违禁词检测接口",summary="敏感词库/违禁词检测接口")
@limiter.limit(minute110)
async def ipinfoProUrl1(request: Request,ip:str=""):
    url=f"{ipinfoProUrl}?key={suapiKey}"
    respone=requests.post(url,json={"ip":ip})
    try:
        if respone.ok:
            data = respone.json()
            res = {
                **data
            }

            return httpStatus(code=status.HTTP_200_OK, message="获取成功", data=res.get("data"))
        return httpStatus()
    except Exception as e:
        return httpStatus()
