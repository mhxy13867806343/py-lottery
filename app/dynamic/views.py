from typing import Optional
from fastapi import APIRouter,Depends,status,Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import time
from dantic.pyBaseModels import DynamicInput
from models.user.model import AccountInputs, UserPosts,ShareSignature
from tool import token as createToken
from tool.classDb import httpStatus
from tool.db import getDbSession
from .operation import getPagenation,getTotal
from models.user.operation import getDynamicList,getDynamicTotal
from .model import DynamicUserShare
dyApp = APIRouter(
    prefix="/h5/dyanmic",
    tags=["用户动态管理"]
)

@dyApp.get('/home/list', description="获取根据条件分页的用户动态列表", summary="获取根据条件分页的用户动态列表")
def getHomeDynamicList(
        session: Session = Depends(getDbSession),
        title: Optional[str] = Query(None, description="标题,可以输入想要搜索的动态标题", alias="title"),
        pageNum: int = Query(1, description="当前页,默认从第1开始", alias="pageNum"),
        pageSize: int = Query(20, description="每页显示条数", alias="pageSize"),
        isStatus: Optional[int] = Query(0, description="0:公开 1:私有", alias="isStatus"),
        deleted: Optional[int] = Query(0, description="是否删除 0:未删除 1:已删除", alias="deleted"),

):
    data=getDynamicList(session=session,title=title, pageNum=pageNum, pageSize=pageSize, status=isStatus, delete=deleted)
    count=getDynamicTotal(session=session,title=title, status=isStatus, delete=deleted)
    result={
       "data":data,
         "total":count,
            "page":pageNum,
            "pageSize":pageSize
    }
    return httpStatus(message="获取成功", data=result, code=status.HTTP_200_OK)


@dyApp.get('/home/user/{uid}/list', description="获取用户动态详情", summary="获取用户动态详情")
def getUserDynamicList(session: Session = Depends(getDbSession),
                       current_user_id: int=Depends(createToken.getNotCurrentUserId),
                       uid: int = Query(None, description="非登录用户id", alias="uid"),
                       title: Optional[str] = Query(None, description="标题,可以输入想要搜索的动态标题", alias="title"),
                       pageNum: int = Query(1, description="当前页,默认从第1开始", alias="pageNum"),
                       pageSize: int = Query(20, description="每页显示条数", alias="pageSize"),
                       isStatus: Optional[int] = Query(0, description="0:公开 1:私有", alias="isStatus"),
                       isDeleted: Optional[int] = Query(0, description="是否删除 0:未删除 1:已删除", alias="isDeleted"),
                      ):
    newStatus:int = isStatus
    newDeleted:int = isDeleted
    if ((current_user_id != uid) or not current_user_id):
        if newStatus==1 or newDeleted==1:
            return httpStatus(message="未删除状态或者未私有状态只能在登录状态才能查看", data={})
    try:
        data = getDynamicList(session=session, uid=uid, title=title, pageNum=pageNum, pageSize=pageSize,
                              status=newStatus, delete=newDeleted)
        count = getDynamicTotal(session=session, uid=uid, title=title,  status=newStatus, delete=newDeleted)
        result = {
            "data": data,
            "total": count,
            "page": pageNum,
            "pageSize": pageSize
        }
        return httpStatus(message="获取成功", data=result, code=status.HTTP_200_OK)
    except SQLAlchemyError as e:
        raise httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="获取动态失败")
@dyApp.post('/share', description="用户动态分享", summary="用户动态分享") #???
def postUserDynamicShare(params: DynamicUserShare, user: AccountInputs = Depends(createToken.pase_token),
                session: Session = Depends(getDbSession)):
    share_type: int = params.share_type
    dynamic_id: int = params.dynamic_id
    if not user.id:
        return httpStatus(message="用户id不能为空", data={})
    if not dynamic_id:
        return httpStatus(message="动态id不能为空", data={})
    if not share_type:
        return httpStatus(message="分享类型不能为空", data={})
    try:
        db = session.query(ShareSignature).filter(ShareSignature.user_id == user.id,
                                                  ShareSignature.count==0
                                                  ).first()
        db.dynamic_id = dynamic_id
        db.user_id = user.id
        db.create_time = int(time.time())
        db.update_time = int(time.time())
        db.type=share_type
        db.count+=1
        session.commit()
        return httpStatus(message="分享动态成功", data={})
        if not db:
            return httpStatus(message="用户不存在,无法分享动态", data={})

    except SQLAlchemyError as e:
        session.rollback()
        raise httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="分享动态失败")
@dyApp.get('/list', description="获取用户动态列表", summary="获取用户动态列表")
def getUserDynamicList(
        session: Session = Depends(getDbSession),
        title: Optional[str] = Query(None, description="标题,可以输入想要搜索的动态标题", alias="title"),
        pageNum: int = Query(1, description="当前页,默认从第1开始", alias="pageNum"),
        pageSize: int = Query(20, description="每页显示条数", alias="pageSize"),
        isStatus: Optional[int] = Query(None, description="0:公开 1:私有", alias="isStatus"),
        isDeleted: Optional[int] = Query(None, description="是否删除 0:未删除 1:已删除", alias="isDeleted"),
        current_user_id: Optional[int] = Depends(createToken.pase_token)  # 这里改为current_user_id
):
    conditions = {"title": title, "current": pageNum, "size": pageSize, "is_deleted": isDeleted}
    if current_user_id:
        # 登录用户可以看到自己的动态，根据状态和删除条件过滤
        conditions["user_id"] = current_user_id
        if isStatus is not None:
            conditions["status"] = isStatus
    else:
        # 未登录用户只能看到公开的未删除的动态
        conditions["is_deleted"] = 0
        conditions["status"] = 0

    data = getPagenation(db=session, model=UserPosts, **conditions)
    total = getTotal(db=session, model=UserPosts, **conditions)

    result = {
        "list": data,
        "total": total,
        "page": pageNum,
        "pageSize": pageSize
    }
    return httpStatus(message="获取成功", data=result, code=status.HTTP_200_OK)
@dyApp.post('/add', description="用户动态发布", summary="用户动态发布")
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
    db = session.query(AccountInputs).filter(AccountInputs.id == user.id).first()
    if not db:
        return httpStatus(message="用户不存在,无法发布动态", data={})
    if db.status == 1:
        return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
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
                             ,status=status,isDisabledTitle=0,isDeleted=0,isTop=0)
        session.add(new_post)
        session.commit()
        return httpStatus(message="发布成功", data={})
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="发布失败", data={})
@dyApp.post('/edit',description="修改用户动态",summary="修改用户动态")
def putUserPosts(params: DynamicInput,user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
     dyId:str=params.id #动态id
     dyContent:str=params.content #动态内容
     dyStatus:int=params.type #0:公开 1:私有
     if not dyId:
            return httpStatus(message="当前id不存在,无法更新动态内容", data={})
     db=session.query(AccountInputs).filter(AccountInputs.id==user.id).first()
     if db is None:
         return httpStatus(message="用户不存在,无法更新动态内容", data={})
     if db.status==1:
        return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
     dyDb=session.query(UserPosts).filter(UserPosts.id==dyId).first()
     if dyDb is None:
         return httpStatus(message="当前动态不存在,无法更新", data={})
     if dyDb.content==dyContent:
            return httpStatus(message="内容未发生变化,无需更新动态", data={})
     try:
         dyDb.content=dyContent
         dyDb.status=dyStatus
         dyDb.update_time=int(time.time())
         session.commit()
         return httpStatus(message="更新成功", data={})
     except SQLAlchemyError as e:
         session.rollback()
         return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="更新失败", data={})
@dyApp.post('/delete',description="删除用户动态",summary="删除用户动态")
def deleteUserPosts(params: DynamicInput,user: AccountInputs = Depends(createToken.pase_token),session: Session = Depends(getDbSession)):
    dyId:str=params.id #动态id
    if not dyId:
        return httpStatus(message="当前动态不存在,无法删除动态内容,请添加动态内容", data={})
    db=session.query(AccountInputs).filter(AccountInputs.id==user.id).first()
    if db is None:
        return httpStatus(message="用户不存在,无法删除动态内容,请添加动态内容", data={})
    if db.status==1:
        return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
    db=session.query(UserPosts).filter(UserPosts.id==dyId).first()
    if db is None:
        return httpStatus(message="当前动态不存在,无法删除,请添加动态内容", data={})
    if db.isTop==1 or db.isDeleted==1 or len(db.content)==0:
        message=f"当前动态为置顶动态或者已删除动态或者动态内容为内,无法删除此动态内容,请添加动态内容"
        return httpStatus(message=message, data={})
    try:
        db.isDeleted=1
        session.commit()
        return httpStatus(message="删除成功", data={},code=status.HTTP_200_OK)
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="删除失败", data={})
@dyApp.post('/top', description="置顶用户动态", summary="置顶用户动态")
def topUserPosts(params: DynamicInput, user: AccountInputs = Depends(createToken.pase_token), session: Session = Depends(getDbSession)):
    dyId = params.id  # 动态id
    if not dyId:
        return httpStatus(message="当前动态不存在,无法置顶动态内容", data={})
    db = session.query(AccountInputs).filter(AccountInputs.id == user.id).first()
    if db is None:
        return httpStatus(message="用户不存在,无法置顶动态内容,请添加动态内容", data={})
    if db.status == 1:
        return httpStatus(message="当前用户已被禁用,请联系管理员", data={})
    db = session.query(UserPosts).filter(UserPosts.id == dyId).first()
    if db is None:
        return httpStatus(message="当前动态不存在,无法置顶,请添加动态内容", data={})
    if not db.content or len(db.content) == 0:
        return httpStatus(message="当前动态内容不存在,无法置顶,请添加动态内容", data={})
    if db.isDeleted == 1:
        message = "当前动态已删除,无法置顶此动态内容,请添加动态内容"
        return httpStatus(message=message, data={})
    # 检查是否已经有置顶的动态
    existing_top = session.query(UserPosts).filter(UserPosts.isTop == 1, UserPosts.id != dyId).first()
    if existing_top:
        # 取消现有的置顶
        existing_top.isTop = 0
    try:
        # 置顶当前动态
        if db.isTop == 1:
            db.isTop = 0
            message = "取消置顶成功"
        else:
            db.isTop = 1
            message = "置顶成功"
        session.commit()
        return httpStatus(message=message, data={},code=status.HTTP_200_OK)
    except SQLAlchemyError as e:
        session.rollback()
        return httpStatus(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="置顶失败", data={})