from fastapi import FastAPI,Depends,Request,status,APIRouter
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles #静态文件操作
from sqlalchemy.dialects.mysql import CHAR,BINARY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import SQLAlchemyError
import uuid
import time
from fastapi.middleware.cors import CORSMiddleware # CORS
from starlette.responses import JSONResponse
from sqlalchemy import create_engine,Column,Integer,String,ForeignKey,func
from sqlalchemy.orm import sessionmaker, relationship,Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import uvicorn
from tool import token as createToken
from tool.statusTool import EXPIRE_TIME
from tool.dbRedis import RedisDB
username="root" # 数据库用户名
password="123456" # 数据库密码
host="localhost" # 数据库地址
port=3306 # 数据库端口
db_name="lottery" # 数据库名

url=f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8"

ENGIN=create_engine(url,echo=True)

LOCSESSION=sessionmaker(bind=ENGIN)
# 从sqlalchemy中创建基类
Base=declarative_base()
from tool.classDb import UUIDType,httpStatus,validate_phone_input,validate_pwd
from tool.defDb import dbSessionCommitClose,isAdminOrTypeOne
from tool.getAjax import getHeadersHolidayUrl
from dantic.pyBaseModels import UserInput, PhoneInput, LotteryInput, UserQcInput, AccountInput, dictQueryExtractor, \
    DictType, DictTypeName, DictTypeParams, AccountInputFirst, DynamicInput


class DictTypes(Base):
    __tablename__ = 'dict'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, default='')
    key = Column(String(30), nullable=False, default='')
    value = Column(String(30), nullable=False, default='')
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    status = Column(Integer, nullable=False, default=0)
    children = relationship("DictTypesChild", backref="dict")
    def __repr__(self):
        return f'<DictTypes {self.children}>'
class DictTypesChild(Base):
    __tablename__ = 'dict_child'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, default='')
    key = Column(String(30), nullable=False, default='')
    value = Column(String(30), nullable=False, default='')
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    parent_id = Column(Integer, ForeignKey('dict.id'))
    status = Column(Integer, nullable=False, default=0)
    def __repr__(self):
        return f'<DictTypesChild {self.parent_id}>'

class AccountInputs(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(100), nullable=False, default='')
    password = Column(String(100), nullable=False, default='')
    type = Column(Integer, nullable=False, default=0)
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    name=Column(String(30),nullable=False,default='管理员')
    posts = relationship("UserPosts", back_populates="user")
    def __repr__(self):
        return f'<AccountInputs {self.account}>'


class UserPosts(Base):
    __tablename__ = 'user_posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    isDisabledTitle=Column(Integer,nullable=False,default=0) #标题不能进行修改创建完了就不能修改 0:不可以修改 1:不可以修改
    title = Column(String(100), nullable=False, default='') # 最多100个字符
    content = Column(String(255), nullable=False, default='')  # 最多255个字符
    create_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    update_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    status = Column(Integer, nullable=False, default=0)
    # 创建与AccountInputs的反向引用，建立一对多关系
    user = relationship("AccountInputs", back_populates="posts")
    def __repr__(self):
        return f'<UserPosts {self.content[:10]}...>'  # 显示内容的前10个字符
class User(Base):
    __tablename__ = 'user'
    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    name = Column(String(30), nullable=False, default='')
    phone = Column(String(11), nullable=False, default='')
    count=Column(Integer,nullable=False,default=2)
    create_time=Column(Integer,nullable=False,default=lambda: int(time.time()))
    last_time = Column(Integer, nullable=False, default=lambda: int(time.time()))
    lottery_records = relationship("LotteryRecord", backref="user")
    paymentAccount=relationship("PaymentAccount",backref="user")
    def __repr__(self):
        return f'<User {self.name}>'


class LotteryRecord(Base):
    __tablename__ = 'lottery_records'
    id = Column(CHAR(36), primary_key=True)
    l_name=Column(String(30),nullable=False,default='')
    user_id = Column(CHAR(36), ForeignKey('user.id'))
    create_time = Column(Integer, nullable=False)
    timestamp = Column(Integer, nullable=False)
class PaymentAccount(Base):
    __tablename__ = 'payment_account'
    id = Column(CHAR(36), primary_key=True)
    user_id = Column(CHAR(36), ForeignKey('user.id'))
    account = Column(String(30), nullable=False, default='')
    create_time = Column(Integer, nullable=False)
    timestamp = Column(Integer, nullable=False)
router = APIRouter(
    prefix="/v1",  # 为这个路由器下的所有路由添加路径前缀 /v1
    tags=["v1"],  # 可选，为这组路由添加标签
)
redis_db = RedisDB()
app = FastAPI()
# 将 router 添加到 app 中
origins = [
"*"

]  #也可以设置为"*"，即为所有。
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)
expires_delta = timedelta(minutes=EXPIRE_TIME)
def getDbSession():
    db = LOCSESSION()
    try:
        yield db
    finally:
        db.close()
@app.middleware("http")
async def allow_pc_only(request: Request, call_next):
    if not request.url.path.startswith("/h5/"):
        user_agent = request.headers.get('User-Agent', '').lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            # 如果检测到是移动设备且不是访问/h5/路径，返回403禁止访问
            return httpStatus(code=status.HTTP_403_FORBIDDEN,message="当前环境不允许进行访问", data={})
        # 对于/h5/路径或非移动设备请求，继续处理
    response = await call_next(request)
    return response



@router.post('/h5/registered',description="h5注册",summary="h5注册")
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
                                    last_time=rTime,name=name,type=1)
        db.add(resultSql)
        db.commit()
        db.flush()
        return httpStatus(code=status.HTTP_200_OK, message="注册成功", data={})
    return httpStatus(message="当前帐号已注册存在,请直接登录", data={})


@router.post('/h5/login', description="登录用户信息", summary="登录用户信息")
def login(user_input: AccountInput, session: Session = Depends(getDbSession)):
    account = user_input.account
    password = user_input.password
    newAccount=f"user-{account}"#redis key
    if not account or not password:
        return httpStatus(message="账号或密码不能为空", data={})
    # 先从Redis尝试获取用户信息
    user_data = redis_db.get(newAccount)
    if user_data:
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
        }
        # 将用户信息保存到Redis
        redis_db.set(newAccount, user_data)  # 注意调整为合适的键值和数据
        return httpStatus(code=status.HTTP_200_OK, message="登录成功", data=user_data)
    except Exception as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="登录失败", data={})
@router.post('/h5/user')
def getUserInfo(user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    redis_key = f"user-{user.account}"  # 构造一个基于用户ID的Redis键

    # 尝试从Redis获取用户信息
    redis_user_data = redis_db.get(redis_key)
    if redis_user_data:
        # 如果在Redis中找到了用户信息，直接使用这些信息构建响应
        data_source = {
            "account": redis_user_data["account"],
            "name": redis_user_data["name"],
            "type": redis_user_data["type"],
            "createTime": redis_user_data["createTime"],
            "lastTime": redis_user_data["lastTime"],
            "id": redis_user_data["sub"],
            "isPermissions": 1
        }
    else:
        user = session.query(AccountInputs).filter(AccountInputs.id == user.id).first()
        if user is None:
            return httpStatus(message="用户不存在", data={})
        data_source = {
            "account": user.account,
            "name": user.name,
            "type": user.type,
            "createTime": user.create_time,
            "lastTime": user.last_time,
            "id": user.id,
            "isPermissions": 1
        }

    return httpStatus(code=status.HTTP_200_OK, message="获取成功", data=data_source)
@router.post('/h5/user/update',description="更新用户信息",summary="更新用户信息")
def updateUserInfo(params: AccountInputFirst, user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    name = params.name
    if not name:
        return httpStatus(message="昵称不能为空", data={})
    db=session.query(AccountInputs).filter(AccountInputs.id==user.id).first()
    if db is None:
        return httpStatus(message="用户不存在,无法更新", data={})
    if db.name==name:
        return httpStatus(message="昵称未发生变化", data={})
    try:
        user.name = name
        session.commit()
        return httpStatus(code=status.HTTP_200_OK, message="更新成功", data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="更新失败", data={})
@router.post('/h5/user/logout',description="用户退出",summary="用户退出")
def logout(user: AccountInputs = Depends(createToken.pase_token)):
    redis_key = f"user-{user.account}"
    redis_db.delete(redis_key)
    return httpStatus(code=status.HTTP_200_OK, message="退出成功", data={})


@router.post('/h5/user/post/dynamic', description="用户动态发布", summary="用户动态发布")
def postUserDynamic(params: DynamicInput, user: AccountInputs = Depends(createToken.pase_token),
                session: Session = Depends(getDbSession)):
    content:str = params.content
    title=params.name
    status:int=params.type #0:公开 1:私有
    if not title:
        return httpStatus(message="标题不能为空", data={})
    if not content:
        return httpStatus(message="动态内容不能为空", data={})
    if len(title) > 100:
        return httpStatus(message="标题不能超过100个字符", data={})
    if len(content) > 255:
        return httpStatus(message="动态内容不能超过255个字符", data={})

    # 查询用户的最近一篇帖子
    latest_post = session.query(UserPosts).filter(UserPosts.user_id == user.id).order_by(
        UserPosts.create_time.desc()).first()
    if latest_post:
        # 检查时间差
        current_time = int(time.time())
        if (current_time - latest_post.create_time) < 30:
            return httpStatus(message="30秒内不允许连续发布", data={})

        # 如果本次发布内容与之前内容相同，则拒绝发布
        if latest_post.content == content:
            return httpStatus(message="发布内容与之前相同，不允许发布", data={})

    # 创建新的动态
    try:
        new_post = UserPosts(title=title,user_id=user.id, content=content, create_time=int(time.time()), update_time=int(time.time())
                             ,status=status,isDisabledTitle=0)
        session.add(new_post)
        session.commit()
        return httpStatus(message="发布成功", data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="发布失败", data={})
@router.put('/h5/user/put/dynamic',description="修改用户动态",summary="修改用户动态")
def putUserPosts(params: DynamicInput,user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
     dyId:str=params.id #动态id
     dyContent:str=params.content #动态内容
     dyStatus:int=params.type #0:公开 1:私有
     if not dyId:
            return httpStatus(message="当前id不存在,无法更新动态内容", data={})

     db=session.query(UserPosts).filter(UserPosts.id==dyId).first()
     if db is None:
         return httpStatus(message="当前动态不存在,无法更新", data={})
     if db.content==dyContent:
            return httpStatus(message="内容未发生变化,无需更新动态", data={})
     try:
         db.content=dyContent
         db.status=dyStatus
         db.update_time=int(time.time())
         session.commit()
         return httpStatus(message="更新成功", data={})
     except SQLAlchemyError as e:
         session.rollback()
         return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="更新失败", data={})


@router.get('/pc/get/user',description="获取用户信息",summary="获取用户信息")
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

@router.get("/h5/festival",description="获取节假日信息",summary="获取节假日信息")
async def root(request: Request)->dict:
    user_agent = request.headers.get('User-Agent')
    headers={"User-Agent": user_agent}
    return {
        "data":{
            "message": "获取成功",
            "result": {
                **getHeadersHolidayUrl(headers=headers),
                "UserAgent": user_agent,

            }
        }
    }
@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=ENGIN)

app.include_router(router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    # uvicorn main.app --reload
    # uvicorn.run(app,host="localhost", port=8000)