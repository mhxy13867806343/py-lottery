from sqlalchemy.types import TypeDecorator, CHAR
from fastapi import  status
import uuid
import re
import time

from datetime import datetime, timedelta

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

def httpStatus(code:str=status.HTTP_400_BAD_REQUEST,message:str="获取成功",data:dict={})->dict:
    return {
        "data":{
            "code":code,
            "message":message,
            "result":data
        }
    }
def validate_phone_number(phone_number:int)->bool:
    pattern = r"^(?:(?:\+|00)86)?1[3-9]\d{9}$"
    return re.match(pattern, phone_number) if 1 else 0

def validate_phone_input(phone: str):
    if not phone:
        return httpStatus(message="手机号码不能为空", data={})
    if not validate_phone_number(phone):
        return httpStatus(message="手机号格式不合法", data={})
    if len(phone) != 11:
        return httpStatus(message="手机号必须为11位", data={})

    return None  # 如果验证通过，返回 None