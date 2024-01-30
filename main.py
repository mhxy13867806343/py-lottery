from fastapi import FastAPI,Depends,Request,status
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
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import uvicorn

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
from tool.classDb import UUIDType,httpStatus,validate_phone_input,get_next_year_timestamp
from tool.getAjax import getHeadersHolidayUrl
from dantic.pyBaseModels import UserInput,PhoneInput,LotteryInput,UserQcInput
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
app = FastAPI()
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



#生成一个通过手机号码查询用户的接口
@app.post('/phone',description="通过手机号码获取信息",summary="通过手机号码获取信息")
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
@app.post('/lottery')
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
@app.post('/login',description="保存未存在的或者获取已存在的用户信息",summary="保存未存在的或者获取已存在的用户信息")
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
@app.get('/')
async def index():
    return {
        "data":{
            "message":"欢迎来到德莱联盟",
            "result":{
                "version":"1.0.0",
                "authorName":"hooks",
                "authorEmail":"869710179@qq.com",
                "createTime":int(time.time()),
                "authorWxid":"aigchooks",
                "authorImg":"static/wx/WechatIMG914.jpg",
            }
        }
    }
@app.get("/festival",description="获取节假日信息",summary="获取节假日信息")
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

@app.post('/paymentAccount')
def paymentAccount(user_input:UserQcInput)->dict:
    phone=user_input.phone
    name=user_input.name
    account=user_input.account
    validation_error = validate_phone_input(phone)
    if validation_error:
        return validation_error
    if not  account:
        return httpStatus(message="支付账号不能为空", data={})
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=ENGIN)
if __name__ == "__main__":
    uvicorn.run(app,host="localhost", port=8000)