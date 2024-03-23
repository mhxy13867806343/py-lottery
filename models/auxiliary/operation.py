from sqlalchemy.orm import Session
from .model import Email

def getEmailList(email:str,session:Session,pageNum:int=1,pageSize:int=20)->list:
    resultSum = (pageNum - 1) * pageSize
    result = session.query(Email).filter(Email.email==email).offset(resultSum).limit(pageSize).all()
    return result

#获取总条数
def getEmailTotal(email:str,session:Session)->int:
    total = session.query(Email).filter(Email.email==email).count()
    return total