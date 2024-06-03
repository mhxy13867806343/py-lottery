from fastapi import APIRouter,Depends,status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta

from tool.dbConnectionConfig import sendBindEmail, getVerifyEmail

from tool.dbTools import getValidate_email
from tool.msg import msg
from .model import AccountInputFirst, AccountInputEamail
from tool.db import getDbSession
from tool import token as createToken
from models.user.model import AccountInputs
from tool.classDb import httpStatus, validate_pwd
from dantic.pyBaseModels import AccountInput
from tool.dbRedis import RedisDB
from tool.statusTool import EXPIRE_TIME

redis_db = RedisDB()
expires_delta = timedelta(minutes=EXPIRE_TIME)
userApp = APIRouter()
@userApp.post('/registered',description="h5注册",summary="h5注册")
def registered(acc:AccountInput,db:Session = Depends(getDbSession)):
    account:str=acc.account
    password:str=acc.password
    if not account or not password:
        return httpStatus(message=msg.get('error2'), data={})
    if not validate_pwd(password):
        return httpStatus(message=msg.get("pwdstatus"), data={})
    existing_account = db.query(AccountInputs).filter(AccountInputs.account == account).first()
    if existing_account is None:
        rTime = int(time.time())
        name=str('--')+str(rTime)+str(account)+str('--')
        password = createToken.getHashPwd(password)
        resultSql = AccountInputs(account=account, password=password, create_time=rTime,
                                    last_time=rTime,name=name,type=1,status=0)
        db.add(resultSql)
        db.commit()
        db.flush()
        return httpStatus(code=status.HTTP_200_OK, message=msg.get('ok0'), data={})
    return httpStatus(message=msg.get("error1"), data={})


@userApp.post('/login', description="登录用户信息", summary="登录用户信息")
def login(user_input: AccountInput, session: Session = Depends(getDbSession)):
    account = user_input.account
    password = user_input.password
    newAccount=f"user-{account}"#redis key
    if not account or not password:
        return httpStatus(message=msg.get("error2"), data={})
    # 先从Redis尝试获取用户信息
    user_data = redis_db.get(newAccount)
    if user_data:
        if user_data.get('status')=="1" or int(user_data.get('status'))==1:
            return httpStatus(message=msg.get('accountstatus'), data={})
        try:
            # 验证token的有效性
            user_id = createToken.pase_token(user_data['token'])
            # 如果提供的账号与Redis中的账号一致，且token有效，认为登录成功
            if user_id and account == user_data["account"]:
                user_data['status']=int(user_data['status'])
                user_data['type']=int(user_data['type'])
                user_data['createTime']=int(user_data['createTime'])
                user_data['lastTime']=int(user_data['lastTime'])
                user_data["email"]=user_data.get("email")
                return httpStatus(code=status.HTTP_200_OK, message="登录成功", data=user_data)
            return httpStatus(message=msg.get("tokenstatus"), data={})
        except Exception as e:
            print(e)
            return httpStatus(message=msg.get("tokenstatus"), data={})
    existing_user = session.query(AccountInputs).filter(AccountInputs.account == account).first()
    if existing_user is None or not createToken.check_password(password, existing_user.password):
        return httpStatus(message=msg.get('error0'), data={})
    if existing_user.status=='1' or int(existing_user.status)==1:
        return httpStatus(message=msg.get('accountstatus'), data={})
    try:
        # 用户验证成功，创建token等操作
        token = createToken.create_token({"sub": str(existing_user.id)}, expires_delta)
        user_data = {
            "token": token,
            "type": int(existing_user.type),
            "account": existing_user.account,
            "createTime": int(existing_user.create_time),
            "lastTime": int(existing_user.last_time),
            "name": existing_user.name,
            "status": int(existing_user.status),
            "email": existing_user.email
        }
        # 将用户信息保存到Redis
        redis_db.set(newAccount, user_data)  # 注意调整为合适的键值和数据
        return httpStatus(code=status.HTTP_200_OK, message=msg.get('login0'), data=user_data)
    except Exception as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=msg.get("login1"), data={})
@userApp.post('/info',description="获取用户信息",summary="获取用户信息")
def getUserInfo(user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    redis_key = f"user-{user.account}"  # 构造一个基于用户ID的Redis键

    # 尝试从Redis获取用户信息
    redis_user_data = redis_db.get(redis_key)
    if redis_user_data:
        if redis_user_data.get('status')==1:
            return httpStatus(message=msg.get('accountstatus'), data={})
        # 如果在Redis中找到了用户信息，直接使用这些信息构建响应
        data_source = {
            "account": redis_user_data["account"],
            "name": redis_user_data["name"],
            "type": redis_user_data["type"],
            "createTime": redis_user_data["createTime"],
            "lastTime": redis_user_data["lastTime"],
            "id": redis_user_data["sub"],
            "isPermissions": 1,
            "email": redis_user_data.get("email"),
            "status": redis_user_data["status"]
        }
    else:
        user = session.query(AccountInputs).filter(AccountInputs.id == user.id).first()
        if user is None:
            return httpStatus(message=msg.get("error3"), data={})
        if user.status==1:
            return httpStatus(message=msg.get('accountstatus'), data={})
        data_source = {
            "account": user.account,
            "name": user.name,
            "type": user.type,
            "createTime": user.create_time,
            "lastTime": user.last_time,
            "id": user.id,
            "isPermissions": 1,
            "status": user.status,
            "email": user.email
        }

    return httpStatus(code=status.HTTP_200_OK, message=msg.get("ok99"), data=data_source)


@userApp.post('/update',description="更新用户信息",summary="更新用户信息")
def updateUserInfo(params: AccountInputFirst, user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    name = params.name
    if not name:
        return httpStatus(message=msg.get("error4"), data={})
    db=session.query(AccountInputs).filter(AccountInputs.id==user.id).first()
    if db is None:
        return httpStatus(message=msg.get("error5"), data={})
    if db.status == 1:
        return httpStatus(message=msg.get('accountstatus'), data={})
    if db.name==name:
        return httpStatus(message=msg.get("error51"), data={})
    try:
        user.name = name
        session.commit()
        return httpStatus(code=status.HTTP_200_OK, message=msg.get("update0"), data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=msg.get("update1"), data={})
@userApp.post('/logout',description="用户退出",summary="用户退出")
def logout(user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    redis_key = f"user-{user.account}"
    db=session.query(AccountInputs).filter(AccountInputs.id==user.id).first()
    if db is None:
        return httpStatus(message=msg.get("loguto0"), data={})
    if db.status == 1:
        return httpStatus(message=msg.get('accountstatus'), data={})
    redis_db.delete(redis_key)
    return httpStatus(code=status.HTTP_200_OK, message=msg.get("login01"), data={})

@userApp.post("/bind",description="绑定用户邮箱",summary="绑定用户邮箱")
def addEmail(params: AccountInputEamail, user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    email = params.email
    if not email:
        return httpStatus(message=msg.get("email00"), data={})
    result:bool=getValidate_email(email)
    if not result:
        return httpStatus(message=msg.get("email01"), data={})
    resultSql = session.query(AccountInputs).filter(AccountInputs.id == user.id)
    if not resultSql.first():
        return httpStatus(message=msg.get("email02"), data={})
    if resultSql.first().status == 1:
        return httpStatus(message=msg.get("accountstatus"), data={})
    count=resultSql.count()
    if count>0:
        return httpStatus(message=msg.get("email021"), data={})
    try:
        sendEmail = sendBindEmail(email)
        print(sendEmail)
        print(dir(sendEmail))
        message = sendEmail.get("message")
        verification_data = sendEmail.get("verification_data")[email]
        code = sendEmail.get("code")
        if message and verification_data and code:
            resultSql.first().email=email
            session.commit()
            return httpStatus(code=status.HTTP_200_OK, message=msg.get("email09901"), data={})
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=msg.get("email09902"), data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=msg.get("email09902"), data={})

@userApp.post("/verify",description="验证用户邮箱",summary="验证用户邮箱")
def verifyEmail(email:str="",code:str="", user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    if not email:
        return httpStatus(message=msg.get("email00"), data={})
    if email!=user.email:
        return httpStatus(message=msg.get("email022"), data={})
    if not code:
        return httpStatus(message=msg.get("email023"), data={})
    result:dict=getVerifyEmail(email, code)
    code=result.get("code")
    message=result.get("message")
    if code!=0:
        return httpStatus(message=message, code=code,data={})
    return httpStatus(code=status.HTTP_200_OK, message=message, data={})


@userApp.post("/resetpwd",description="重置密码",summary="重置密码")
def resetPwd(email:str="",code:str="",password:str="", user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    if not email:
        return httpStatus(message=msg.get("email00"), data={})
    if email!=user.email:
        return httpStatus(message=msg.get("email022"), data={})
    if not password:
        return httpStatus(message=msg.get("email09903"), data={})
    if not validate_pwd(password):
        return httpStatus(message=msg.get("pwdstatus"), data={})
    if not code:
        return httpStatus(message=msg.get("email09904"), data={})
    result: dict = getVerifyEmail(email, code)
    code = result.get("code")
    message = result.get("message")
    if code != 0:
        return httpStatus(message=message, code=code, data={})
    if user.status==1:
        return httpStatus(message=msg.get("accountstatus"), data={})
    try:
        resultSql = session.query(AccountInputs).filter(AccountInputs.id == user.id)
        if not resultSql.first(): #找不到用户
            return httpStatus(message=msg.get("error3"), data={})
        if resultSql.first().status == 1:
            return httpStatus(message=msg.get("accountstatus"), data={})
        if not resultSql.first().email  or len(resultSql.first().email)==0:
            return httpStatus(message=msg.get("email001"), data={})
        user.password = createToken.getHashPwd(password)
        session.commit()
        return httpStatus(code=status.HTTP_200_OK, message=msg.get("updatdpwd"), data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=msg.get("updatdpwd001"), data={})