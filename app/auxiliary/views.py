from fastapi import APIRouter,Depends,status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta
from .model import AuxiliaryInputFirst,AuxiliaryInput
from models.auxiliary.operation import getEmailList,getEmailTotal
from tool.db import getDbSession
from models.auxiliary.model import Email
from tool.classDb import httpStatus, validate_email_str,validate_encrypt_email
from tool.dbRedis import RedisDB
from tool.statusTool import EXPIRE_TIME
from .tools import sendEmail,isSend
redis_db = RedisDB()
expires_delta = timedelta(minutes=EXPIRE_TIME)
emailApp = APIRouter(
    prefix="/h5/auxiliary",
    tags=["辅助管理"]
)
@emailApp.get('/{email}',description="邮箱列表",summary="邮箱列表")
async def email_list(email:str,session:Session = Depends(getDbSession)):
    if not email:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="邮箱不能为空",data={})
    try:
        #searchEmail 加密下8697****9@qq.com


        result={
            "searchEmail":validate_encrypt_email(email),
            "total":getEmailTotal(email,session),
            "data":getEmailList(email,session)
        }
        return httpStatus(code=status.HTTP_200_OK,message="获取成功",data=result)
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="获取失败",data={})
@emailApp.post('/send/email',description="发送邮箱",summary="发送邮箱")
def send_email(aed:AuxiliaryInputFirst,session:Session = Depends(getDbSession)):
    title:str=aed.title
    email:str=aed.email
    content:str=aed.content
    if not email:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="邮箱不能为空",data={})
    if not validate_email_str(email):
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="邮箱格式不正确",data={})
    if not content:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="内容不能为空",data={})
    db_email = session.query(Email).filter(Email.email == email).all()
    if len(db_email) > 50:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="当前最多只能发送50封邮件",data={})
    try:
        if isSend:
            rTime = int(time.time())
            sendEmail(title=title,content=content,from_email=email)
            resultSql = Email(email=email, title=title, content=content, create_time=rTime)
            session.add(resultSql)
            session.commit()
            return httpStatus(code=status.HTTP_200_OK,message="发送成功",data={})
        else:
            return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="发送失败",data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_400_BAD_REQUEST,message="发送失败",data={})

