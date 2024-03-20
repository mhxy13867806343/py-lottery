from fastapi import APIRouter,Depends,status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from datetime import datetime, timedelta
from .model import AccountInputFirst
from tool.db import getDbSession
from tool import token as createToken
from models.user.model import AccountInputs
from tool.classDb import httpStatus, validate_pwd
from dantic.pyBaseModels import AccountInput
from tool.dbRedis import RedisDB
from tool.statusTool import EXPIRE_TIME

redis_db = RedisDB()
expires_delta = timedelta(minutes=EXPIRE_TIME)
userApp = APIRouter(
    prefix="/h5/user",
    tags=["用户信息管理"]
)
@userApp.post('/registered',description="h5注册",summary="h5注册")
def registered(acc:AccountInput,db:Session = Depends(getDbSession)):
    account:str=acc.account
    password:str=acc.password
    if not account or not password:
        return httpStatus(message="帐号或密码不能为空", data={})
    if not validate_pwd(password):
        msg:str="密码强度太弱啦,第我位字符必须以字母或特殊字符开头，最少6位，包括至少1个大写字母，1个小写字母，1个数字，1个特殊字符"
        return httpStatus(message=msg, data={})
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
        return httpStatus(code=status.HTTP_200_OK, message="注册成功", data={})
    return httpStatus(message="当前帐号已注册存在,请直接登录", data={})


@userApp.post('/login', description="登录用户信息", summary="登录用户信息")
def login(user_input: AccountInput, session: Session = Depends(getDbSession)):
    account = user_input.account
    password = user_input.password
    newAccount=f"user-{account}"#redis key
    if not account or not password:
        return httpStatus(message="账号或密码不能为空", data={})
    # 先从Redis尝试获取用户信息
    user_data = redis_db.get(newAccount)
    if user_data:
        if user_data.status==1:
            return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
        try:
            # 验证token的有效性
            user_id = createToken.pase_token(user_data['token'])
            # 如果提供的账号与Redis中的账号一致，且token有效，认为登录成功
            if user_id and account == user_data["account"]:
                return httpStatus(code=status.HTTP_200_OK, message="登录成功", data=user_data)
            return httpStatus(message="登录信息已失效，请重新登录", data={})
        except Exception as e:
            print(e)
            return httpStatus(message="登录信息已失效，请重新登录", data={})
    existing_user = session.query(AccountInputs).filter(AccountInputs.account == account).first()
    if existing_user is None or not createToken.check_password(password, existing_user.password):
        return httpStatus(message="账号或密码错误，请重新输入", data={})
    if existing_user.status==1:
        return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
    try:
        # 用户验证成功，创建token等操作
        token = createToken.create_token({"sub": str(existing_user.id)}, expires_delta)
        user_data = {
            "token": token,
            "type": existing_user.type,
            "account": existing_user.account,
            "createTime": existing_user.create_time,
            "lastTime": existing_user.last_time,
            "name": existing_user.name,
            "status": existing_user.status
        }
        # 将用户信息保存到Redis
        redis_db.set(newAccount, user_data)  # 注意调整为合适的键值和数据
        return httpStatus(code=status.HTTP_200_OK, message="登录成功", data=user_data)
    except Exception as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="登录失败", data={})
@userApp.post('/info',description="获取用户信息",summary="获取用户信息")
def getUserInfo(user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    redis_key = f"user-{user.account}"  # 构造一个基于用户ID的Redis键

    # 尝试从Redis获取用户信息
    redis_user_data = redis_db.get(redis_key)
    if redis_user_data:
        if redis_user_data.status==1:
            return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
        # 如果在Redis中找到了用户信息，直接使用这些信息构建响应
        data_source = {
            "account": redis_user_data["account"],
            "name": redis_user_data["name"],
            "type": redis_user_data["type"],
            "createTime": redis_user_data["createTime"],
            "lastTime": redis_user_data["lastTime"],
            "id": redis_user_data["sub"],
            "isPermissions": 1,
            "status": redis_user_data["status"]
        }
    else:
        user = session.query(AccountInputs).filter(AccountInputs.id == user.id).first()
        if user is None:
            return httpStatus(message="用户不存在", data={})
        if user.status==1:
            return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
        data_source = {
            "account": user.account,
            "name": user.name,
            "type": user.type,
            "createTime": user.create_time,
            "lastTime": user.last_time,
            "id": user.id,
            "isPermissions": 1,
            "status": user.status
        }

    return httpStatus(code=status.HTTP_200_OK, message="获取成功", data=data_source)

@userApp.get('/testinfo',description="获取用户信息",summary="获取用户信息")
async def getIndexauthorUser():
    return {
        "data":{
            "message":"欢迎来到德莱联盟",
            "data":{
                "version":"1.0.0",
                "authorName":"hooks",
                "authorEmail":"869710179@qq.com",
                "createTime":int(time.time()),
                "authorWxid":"aigchooks",
                "authorImg":"static/wx/WechatIMG914.jpg",
            }
        }
    }
@userApp.post('/update',description="更新用户信息",summary="更新用户信息")
def updateUserInfo(params: AccountInputFirst, user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    name = params.name
    if not name:
        return httpStatus(message="昵称不能为空", data={})
    db=session.query(AccountInputs).filter(AccountInputs.id==user.id).first()
    if db is None:
        return httpStatus(message="用户不存在,无法更新", data={})
    if db.status == 1:
        return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
    if db.name==name:
        return httpStatus(message="昵称未发生变化", data={})
    try:
        user.name = name
        session.commit()
        return httpStatus(code=status.HTTP_200_OK, message="更新成功", data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="更新失败", data={})
@userApp.post('/logout',description="用户退出",summary="用户退出")
def logout(user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    redis_key = f"user-{user.account}"
    db=session.query(AccountInputs).filter(AccountInputs.id==user.id).first()
    if db is None:
        return httpStatus(message="用户不存在,无法退出", data={})
    if db.status == 1:
        return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
    redis_db.delete(redis_key)
    return httpStatus(code=status.HTTP_200_OK, message="退出成功", data={})
