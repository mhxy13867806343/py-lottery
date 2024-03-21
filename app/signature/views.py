from fastapi import APIRouter,Depends,status,Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from tool import token as createToken
from models.user.model import Signature,AccountInputs
from tool.classDb import httpStatus
from tool.db import getDbSession
from .model import SignatureFirst
signatureApp = APIRouter(
    prefix="/h5/signature",
    tags=["用户个性签到管理"]
)
@signatureApp.get('/{userId}', description="获取用户个性签名", summary="获取用户个性签名")
def get_signature_first(userId: int=None,db: Session = Depends(getDbSession),
                        user: AccountInputs = Depends(getDbSession),
current_user: AccountInputs = Depends(createToken.pase_token)
                        ):
    if not userId:
        return httpStatus(message="用户id不能为空", data={})
    signature = db.query(Signature).filter(Signature.user_id ==userId).first()
    if not signature:
        return httpStatus(message="用户签名不存在,请先添加25个字内签名吧", data={},code=status.HTTP_200_OK)
    if signature.user.status==1:
        return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
    return httpStatus(message="获取成功", data=signature, code=status.HTTP_200_OK)


@signatureApp.post('/add', description="用户个性签名添加", summary="用户个性签名添加",)
def add_signature(signature: SignatureFirst, db: Session = Depends(getDbSession)):
    return httpStatus(message="添加成功", data=signature, code=status.HTTP_200_OK)