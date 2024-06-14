from app.signature.model import SignatureInput, SignatureOutput
from models.user.model import Signature, AccountInputs
from fastapi import APIRouter,Depends,status
from sqlalchemy.exc import SQLAlchemyError
from tool.classDb import httpStatus, validate_pwd
from sqlalchemy.orm import Session
from tool.db import getDbSession
from tool import token as createToken
from tool.msg import msg
import  time
signatureApp = APIRouter()

@signatureApp.post('/add', description="添加签名内容", summary="添加签名内容")
def addSignature(ub: SignatureInput,uid: AccountInputs = Depends(createToken.pase_token), session: Session = Depends(getDbSession)):
    if not uid:
        return httpStatus(message=msg.get('error31'), data={},code=status.HTTP_401_UNAUTHORIZED)
    content=ub.content
    maxlenth:int=64
    if not uid:
        return httpStatus(status.HTTP_400_BAD_REQUEST, message=msg.get("error31"),data={})
    if len(content) > maxlenth:
        return httpStatus(status.HTTP_400_BAD_REQUEST, message=msg.get("signatur499"), data={})
    db=session.query(AccountInputs).filter(AccountInputs.id==uid).first()
    if not db or db.status==1:
        return httpStatus(status.HTTP_400_BAD_REQUEST, message=msg.get("error31"),data={})

    existing_signature = session.query(Signature).filter(Signature.user_id == db.id).first()

    if existing_signature :

        if existing_signature.content==content:
            return httpStatus(code=status.HTTP_400_BAD_REQUEST, message=msg.get("signatur999"), data={})

    try:
        if existing_signature and existing_signature.created_time:
            # 更新现有的签名
            existing_signature.content = content
            existing_signature.last_time = int(time.time())
        else:
            # 创建新的签名
            new_signature = Signature(content=content, user_id=db.id, last_time=int(time.time()),
                                      created_time=int(time.time()))
            session.add(new_signature)

        session.commit()
        signaturMsg=msg.get("signatur202") if existing_signature and existing_signature.created_time else msg.get("signatur502")
        return httpStatus(code=status.HTTP_200_OK, message=signaturMsg, data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_400_BAD_REQUEST, message=f"数据库错误: {str(e)}", data={})


@signatureApp.get('/connentId', description="获取签名内容", summary="获取签名内容")
def getSignature(user: AccountInputs = Depends(createToken.pase_token), session: Session = Depends(getDbSession)):
    if not user:
        return httpStatus(message=msg.get('error31'), data={},code=status.HTTP_401_UNAUTHORIZED)
    db=session.query(AccountInputs).filter(AccountInputs.id==user).first()
    if db.status == 1:
        return httpStatus(code=status.HTTP_400_BAD_REQUEST, message="用户被禁用")

    result = session.query(Signature).filter(Signature.user_id == user).first()
    if not result:
        return httpStatus(code=status.HTTP_200_OK, message=msg.get("signatur100"),
                          data={
                                "content": "",
                                "createdTime": 0,
                                "lastTime": 0
                          }
                          )
    return httpStatus(code=status.HTTP_200_OK, message=msg.get("signatur100"),
                      data={
                          "content": result.content,
                          "createdTime":result.created_time,
                          "lastTime": result.last_time
                      }
                      )
