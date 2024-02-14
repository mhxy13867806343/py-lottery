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
from tool.classDb import UUIDType,httpStatus,validate_phone_input,get_next_year_timestamp,createUuid,getListAll,getListAllTotal
from tool.defDb import dbSessionCommitClose
from tool.getAjax import getHeadersHolidayUrl
from dantic.pyBaseModels import UserInput,PhoneInput,LotteryInput,UserQcInput,AccountInput,dictQueryExtractor,DictType,DictTypeName,DictTypeParams


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
    def __repr__(self):
        return f'<AccountInputs {self.account}>'
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
@router.get('/pc/dict/search', description="获取模糊搜索字典信息", summary="获取模糊搜索字典信息")
def getDictSearch(d: DictType = Depends(DictTypeName), db: Session = Depends(getDbSession)):
    if d.page<1:
        return httpStatus(message="页码不能小于1", data={})
    if d.limit<1:
        return httpStatus(message="每页显示数量不能小于1", data={})
    result = getListAll(db, DictTypes, d.name,d.status, d.page, d.limit)
    child = getListAll(db, DictTypesChild, d.name,d.status, d.page, d.limit)
    for item in result:
        item.children=child
    data={
        "page": d.page,
        "limit": d.limit,
        "data":result,
        "total": getListAllTotal(db, DictTypes, d.name,d.status),

    }
    return httpStatus(code=status.HTTP_200_OK, message="查询成功",data=data)
@router.get('/pc/dict', description="获取某个字典信息", summary="获取某个字典信息")
def getDict(d: DictType = Depends(dictQueryExtractor), db: Session = Depends(getDbSession)):
    if not d.name:
        return httpStatus(message="字典名称不能为空", data={})
    query = db.query(DictTypes).filter(DictTypes.status == 0)  # 这里加入了对status的过滤
    if d.name:
        query = query.filter(DictTypes.name == d.name)
    if d.key:
        query = query.filter(DictTypes.key == d.key)
    if d.value:
        query = query.filter(DictTypes.value == d.value)
    first = query.first()
    if not first:
        return httpStatus(message=f"未找到相关字典{d.name}", data={})
    data = {
        "id": first.id,
        "parent_id": first.id,
        "name": first.name,
        "children": db.query(DictTypesChild).filter(DictTypesChild.parent_id == first.id, DictTypesChild.status == 0).all(),  # 这里加入了对status的过滤
        "key": first.key,
        "value": first.value,
        "create_time": first.create_time,
        "timestamp": int(time.time())
    }
    return httpStatus(code=status.HTTP_200_OK, message="查询成功", data=data)


@router.post('/pc/parentDict', description="修改父字典信息", summary="修改父字典信息")
@dbSessionCommitClose(db=Depends(getDbSession))
def saveParidDict(d: DictType = Depends(DictTypeParams), db: Session = Depends(getDbSession)):
    # 检查必要字段
    if not d.parent_id:
        return httpStatus(message="当前字典id不能为空,无法修改", data={})
    if not (d.name and d.key and d.value and d.status is not None):
        return httpStatus(message="字典名称、key、value和状态值不能为空", data={})
    if d.status < 0 or d.status > 1:
        return httpStatus(message="状态值不合法", data={})

    dbResult = db.query(DictTypes).filter(DictTypes.id == d.parent_id).first()
    if not dbResult:
        return httpStatus(message="未找到相关字典,不能进行修改操作", data={})

    # 检查是否有字段需要更新
    update_needed = (
        dbResult.name != d.name or
        dbResult.key != d.key or
        dbResult.value != d.value or
        dbResult.status != d.status
    )

    if not update_needed:
        return httpStatus(message="没有字段变更，无需修改", data={})


    dbResult.name = d.name
    dbResult.key = d.key
    dbResult.value = d.value
    dbResult.status = d.status
    db.commit()
    return httpStatus(message="修改成功", data={})

@router.post('/pc/dictChild', description="保存字典下级信息", summary="保存字典下级信息")
@dbSessionCommitClose(db=Depends(getDbSession))
def saveDictChild(d: DictType, db: Session = Depends(getDbSession))->dict:
    if not d.name or not d.key or not d.value:
        return httpStatus(message="字典名称或者字典key或者字典value不能为空", data={})

    if d.parent_id:
        parent = db.query(DictTypes).filter(DictTypes.id == d.parent_id).first()
        if not parent:
            raise httpStatus(message="父字典未找到")

        # 检查是否已存在相同的子字典

        existing_child = db.query(DictTypesChild)
        if d.name:
            query = existing_child.filter(DictTypesChild.name == d.name)
        if d.key:
            query = existing_child.filter(DictTypesChild.key == d.key)
        if d.value:
            query = existing_child.filter(DictTypesChild.value == d.value)
        first = query.first()
        if first:
            # 如果已存在相同的子字典，则不允许添加
            return httpStatus( message="相同的子字典已存在，不允许重复添加")

        # 如果不存在相同的子字典，则添加新的子字典
        new_child = DictTypesChild(name=d.name, key=d.key, value=d.value, parent_id=d.parent_id)
        db.add(new_child)
        db.commit()
        db.refresh(new_child)
        return httpStatus(message="字典添加成功", code=status.HTTP_200_OK, data={
            "id": new_child.id, "id": new_child.id,
            "name": new_child.name,
            "key": new_child.key,
            "value": new_child.value
        })

    else:
        return httpStatus(message="父字典ID不能为空")


@router.post('/pc/login',description="登录",summary="登录")
@dbSessionCommitClose(db=Depends(getDbSession))
def pcLogin(acc:AccountInput,db:Session = Depends(getDbSession)):
    account=acc.account
    password=acc.password
    if not account or not password:
        return httpStatus(message="帐号或密码不能为空", data={})
    existing_account = db.query(AccountInputs).filter(AccountInputs.account == account).first()

    if existing_account is None:
        if account!='admin':
            return httpStatus(code=status.HTTP_400_BAD_REQUEST, message="只能管理员帐号才能帮您进行注册哦,请联系管理员进行注册哦", data={})

        regTime = int(time.time())
        accountCreated = password + str(regTime)
        new_account = AccountInputs(account=account, password=accountCreated, create_time=regTime,
                                    last_time=regTime)
        db.add(new_account)
        db.commit()
        db.flush()
        return httpStatus(code=status.HTTP_200_OK, message="注册成功", data={})
    if existing_account.type!=0:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST, message="当前帐号权限为已被限制登录,请使用管理员账号登录", data={})
    else:
        if existing_account.account!='admin':
            return httpStatus(code=status.HTTP_200_OK, message="您的帐号不属于管理员权限,请联系管理员添加权限操作", data={})
        token = createToken.create_token({"sub": str(existing_account.id)}, expires_delta)
        data={
            "token":token,
            "type":existing_account.type,
            "account":existing_account.account,
            "createTime":existing_account.create_time,
            "lastTime":existing_account.last_time,
            "name":existing_account.name,
        }
        return httpStatus(code=status.HTTP_200_OK, message="登录成功", data=data)

#生成一个通过手机号码查询用户的接口
@router.post('/h5/phone',description="通过手机号码获取信息",summary="通过手机号码获取信息")
def phone(user_phone:PhoneInput):
    phone=user_phone.phone

    validation_error = validate_phone_input(phone)
    if validation_error:
        return validation_error
    session=LOCSESSION()
    existing_user = session.query(User).filter(User.phone == phone).first()
    if existing_user:
        # 直接通过用户获取抽奖记录
        records_data = [{
            "id": record.id,
            "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            # 添加其他你需要返回的字段
        } for record in existing_user.lottery_records]

        return httpStatus(code=status.HTTP_200_OK, message="获取成功", data=records_data)
    else:
        return httpStatus(code=status.HTTP_200_OK, message="您还没有进行抽奖操作呢,快去抽奖吧", data={})
@router.post('/h5/lottery')
def lottery(user_input: LotteryInput):
    name = user_input.name
    phone = user_input.phone
    last_time = user_input.last_time
    validation_error = validate_phone_input(phone)
    if not name or not phone:
        return httpStatus(message="姓名不能为空", data={})
    if validation_error:
        return validation_error

    session = LOCSESSION()
    user = session.query(User).filter(User.name == name, User.phone == phone).first()
    if not user:
        return httpStatus(message="未找到相关用户呢", data={})
    if user and user.count <= 0:
        next_year_timestamp = get_next_year_timestamp()
        return httpStatus(
            code=status.HTTP_200_OK,
            message="您的抽奖次数已经用完了呢",
            data={
                "count": user.count,
                "lastTime": next_year_timestamp,  # 下一年的时间戳
                "createTime": user.create_time  # 已经是时间戳
            }
        )
    try:
        user.count-=1
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(message="抽奖失败", data={})
    finally:
        session.close()
@router.post('/h5/login',description="保存未存在的或者获取已存在的用户信息",summary="保存未存在的或者获取已存在的用户信息")
def save(user_input: UserInput):
    name=user_input.name
    phone=user_input.phone

    validation_error = validate_phone_input(phone)
    if not name or not phone:
        return httpStatus( message="姓名不能为空", data={})
    if validation_error:
        return validation_error
    session = LOCSESSION()
    user_count = session.query(func.count(User.id)).scalar()
    if user_count >= 10:
        return httpStatus(message="用户数量已经超过10个", data={})

    existing_user = session.query(User).filter(User.name == name, User.phone == phone).first()
    if existing_user:
        # 如果用户存在，认为是登录
        return httpStatus(code=status.HTTP_200_OK, message="登录成功", data={})
    else:
        # 如果用户不存在，创建一个新用户
        new_user = User(name=name, phone=phone,create_time=int(time.time()))
        session.add(new_user)
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()  # 发生异常时回滚事务
            return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="保存失败", data={})
        finally:
            session.close()  # 确保会话在结束时关闭

        return httpStatus(code=status.HTTP_200_OK,message="保存成功",data={})
@router.get('/')
async def index():
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

@router.post('/h5/paymentAccount')
def paymentAccount(user_input:UserQcInput)->dict:
    phone=user_input.phone
    name=user_input.name
    account=user_input.account
    validation_error = validate_phone_input(phone)
    if validation_error:
        return validation_error
    if not  account:
        return httpStatus(message="支付账号不能为空", data={})
@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=ENGIN)

app.include_router(router)
if __name__ == "__main__":
    uvicorn.run(app,host="localhost", port=8000)