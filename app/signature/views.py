from fastapi import APIRouter,Depends,status,Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from tool import token as createToken
from tool.userLogin import isLogin
from models.user.model import Signature,AccountInputs
from tool.classDb import httpStatus
from tool.db import getDbSession
from .model import SignatureFirst
signatureApp = APIRouter(
    prefix="/h5/signature",
    tags=["用户个性签名管理"]
)
@signatureApp.get('/info', description="获取用户个性签名", summary="获取用户个性签名")
def get_signature_first(db: Session = Depends(getDbSession),
                    user: AccountInputs = Depends(createToken.pase_token)
                        ):
    if isLogin(user):
        signature = db.query(Signature).filter(Signature.user_id == user.id).first()
        if not signature:
            return httpStatus(message="用户签名不存在,请先添加25个字内签名吧", data={}, code=status.HTTP_200_OK)
        if signature.user.status == 1:
            return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
        return httpStatus(message="获取成功", data=signature, code=status.HTTP_200_OK)


@signatureApp.post('/add', description="用户个性签名添加", summary="用户个性签名添加",)
def add_signature(signature: SignatureFirst, db: Session = Depends(getDbSession),
                  user: AccountInputs = Depends(createToken.pase_token)
                  ):
    if isLogin(user):
        signature_db = Signature(user_id=user.id, signature=signature.content)
        db.add(signature_db)
        try:
            db.commit()
            return httpStatus(message="添加成功", code=status.HTTP_200_OK)
        except SQLAlchemyError as e:
            db.rollback()
            return httpStatus(message="添加失败")
@signatureApp.post('/update', description="用户个性签名更新", summary="用户个性签名更新",)
def update_signature(signature: SignatureFirst, db: Session = Depends(getDbSession),
                  user: AccountInputs = Depends(createToken.pase_token)
                  ):
    if isLogin(user):
        signature_db = db.query(Signature).filter(Signature.user_id == user.id).first()
        signature_db.signature = signature.content
        try:
            db.commit()
            return httpStatus(message="更新成功", code=status.HTTP_200_OK)

        except SQLAlchemyError as e:
            db.rollback()
            return httpStatus(message="更新失败")