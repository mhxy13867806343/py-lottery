from typing import Optional, List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta
from .model import AuxiliaryInputFirst, AuxiliaryInputPostNunSize, AuxiliaryCopyInput
from models.auxiliary.operation import getEmailList,getEmailTotal
from tool.db import getDbSession
from models.auxiliary.model import Email, CopyEmail
from tool.classDb import httpStatus, validate_email_str,validate_encrypt_email
from tool.statusTool import EXPIRE_TIME
from .tools import sendEmail,isSend,generateEmailId
from tool.takw import getArgsKwArgsResult
expires_delta = timedelta(minutes=EXPIRE_TIME)
emailApp = APIRouter(
    prefix="/h5/auxiliary",
    tags=["辅助管理"]
)
@emailApp.get('/list/email',description="邮箱列表",summary="邮箱列表")
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
@emailApp.post('/send/email',description="发送邮箱",summary="发送邮箱")
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
@emailApp.get('/copy/list/{id}',description="克隆邮箱列表",summary="克隆邮箱列表")
def getCopyEmailList(id:int,session:Session = Depends(getDbSession)):
    if id=='' or id is None:
        return httpStatus(message="id不能为空", data={})
    db_email = session.query(CopyEmail).filter(CopyEmail.email_id == id).all()
    db_count = session.query(CopyEmail).filter(CopyEmail.email_id == id).count()
    data={
        "data":db_email,
        "total":db_count
    }
    return httpStatus(data=data,code=status.HTTP_200_OK,message="获取成功")
@emailApp.post('/send/email/copy',description="克隆邮箱",summary="克隆邮箱")
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