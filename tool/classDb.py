from typing import Tuple, List
from sqlalchemy import or_

from sqlalchemy.types import TypeDecorator, CHAR
from fastapi import  status
import uuid
import re
import time
import hashlib
from datetime import datetime, timedelta

# 通用工具类 正则表达式
toolReg={
    "phone_regex":r"^(?:(?:\+|00)86)?1[3-9]\d{9}$",
    "pwd_regex": r"^(?=[a-zA-Z!@#$%^&*? ])(?=\S{6,})(?=\S*\d)(?=\S*[A-Z])(?=\S*[a-z])(?=\S*[!@#$%^&*? ])\S*$"
}
def get_next_year_timestamp():
    current_time = datetime.now()
    next_year_date = current_time.replace(year=current_time.year + 1)
    return int(time.mktime(next_year_date.timetuple()))
class UUIDType(TypeDecorator):
    impl = CHAR

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, uuid.UUID):
            return str(value)
        else:
            return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

def httpStatus(code:int=status.HTTP_400_BAD_REQUEST,message:str="获取成功",data:dict={})->dict:
    return {
        "data":{
            "code":code,
            "message":message,
            "result":data
        }
    }
def validate_phone_number(phone_number:int)->bool:
    return validateReg("phone_regex",phone_number)
#密码强度校验，最少6位，包括至少1个大写字母，1个小写字母，1个数字，1个特殊字符
def validate_pwd(pwd_str:str)->bool:
    return validateReg("pwd_regex",pwd_str)

def validateReg(reg:str,txt:str)->bool:
    pattern = toolReg[reg]
    return re.match(pattern, txt) if 1 else 0


def validate_phone_input(phone: str)->dict or None:
    if not phone:
        return httpStatus(message="手机号码不能为空", data={})
    if not validate_phone_number(phone):
        return httpStatus(message="手机号格式不合法", data={})
    if len(phone) != 11:
        return httpStatus(message="手机号必须为11位", data={})

    return None  # 如果验证通过，返回 None

def createUuid(name,time,pwd):
    data="{}{}{}".format(name,time,pwd)
    d=uuid.uuid5(uuid.NAMESPACE_DNS, data)
    return d



def createMd5Pwd(pwd:str):
    m = hashlib.md5()
    m.update(pwd.encode('utf-8'))
    return m.hexdigest()


def getListAll(db=None, cls=None, name: str = '', status: int = 0, pageNo: int = 1, pageSize: int = 20):
    size = (pageNo - 1) * pageSize

    # 如果name为空字符串，即没有提供搜索关键词，则忽略name的筛选条件
    if name:
        result = db.query(cls).filter(or_(cls.name.like(f"%{name}%"), cls.status == status)).offset(size).limit(
            pageSize).all()
    else:  # 如果没有提供name，只根据status筛选
        result = db.query(cls).filter(cls.status == status).offset(size).limit(pageSize).all()

    return result


def getListAllTotal(db=None, cls=None, name: str = '', status: int = 0) -> int:
    # 类似地处理总数查询
    if name:
        count = db.query(cls).filter(or_(cls.name.like(f"%{name}%"), cls.status == status)).count()
    else:
        count = db.query(cls).filter(cls.status == status).count()

    return count
