#密码加密
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt,JWTError
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
load_dotenv()
pwdContext=CryptContext(schemes=['bcrypt'], deprecated='auto')#密码加密
SECRET_KEY = os.getenv('SECRET_KEY',None)

ALGORITHM= "HS256"

oauth_scheme= OAuth2PasswordBearer(tokenUrl="login")

def getHashPwd(password:str):
    return pwdContext.hash(password)
def check_password(plain_password:str, hashed_password:str):
    """
    验证明文密码和哈希密码是否匹配。
    :param plain_password: 用户输入的明文密码
    :param hashed_password: 数据库中存储的哈希密码
    :return: 密码是否匹配的布尔值
    """
    # 将明文密码编码为bytes，然后与存储的哈希密码进行比较
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#生成token用户信息，过期时间
def create_token(data:dict,expires_delta):
    if expires_delta:
        expire=datetime.utcnow()+expires_delta
    else:
        expire=datetime.utcnow()+timedelta(minutes=30)
    data.update({"exp":expire})
    token= jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token
#解构token
def pase_token(token:str=Depends(oauth_scheme)):
    token_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                  detail={
                        "code": status.HTTP_401_UNAUTHORIZED,
                        "msg": "用户信息已过期或者token错误",
                  },
                    headers={"WWW-Authenticate": "Bearer"}
                  )
    try:
        jwk_data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id = jwk_data.get("sub")
        if id is None or id == "":
            raise token_exception
    except JWTError as e:
        raise token_exception

    return id