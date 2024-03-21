from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
from models.user.model import UserPosts
from sqlalchemy.orm import Session
from typing import Generic, List, TypeVar, Optional,Type
from pydantic.generics import GenericModel

T = TypeVar('T')

class Pagination(GenericModel, Generic[T]):
    data: List[T]
    total: int
    current: int
    size: int


def get_pagination(db: Session, model: Type[T], current: int = 1, size: int = 20, **kwargs) -> Pagination[T]:
    base_query = db.query(model)

    # 处理是否获取所有用户的帖子，这会覆盖user_id的条件
    isAll = kwargs.pop('isAll', None)
    if isAll:
        if isAll == 1:
            pass  # 获取所有用户的帖子，不添加user_id过滤条件
        else:
            # 添加特定user_id的过滤条件，这里假设isAll不为1
            user_id = kwargs.get('user_id')
            if user_id:
                base_query = base_query.filter(model.id == user_id)
    else:
        # 没有提供isAll时，如果提供了user_id，则过滤特定用户的帖子
        user_id = kwargs.get('user_id')
        if user_id:
            base_query = base_query.filter(model.id == user_id)

    # 构建其他查询条件
    query_conditions = []
    for key, value in kwargs.items():
        if hasattr(model, key) and value is not None:
            attribute = getattr(model, key)
            if isinstance(value, str) and "%" in value:  # 模糊查询
                query_conditions.append(attribute.like(value))
            else:
                query_conditions.append(attribute == value)

    if query_conditions:
        base_query = base_query.filter(and_(*query_conditions))

    total = base_query.count()
    _sum = (current - 1) * size
    items = base_query.offset(_sum).limit(size).all()

    return Pagination[T](
        data=items,
        total=total,
        current=current,
        size=size
    )


#获取分页数据
def getPagenation(db:Session,model=None,user_id:int=None,title:str="",current:int=1,size:int=20,
                  status:int=0, is_deleted:int=0,isAll=0

                  )->[UserPosts]:
    pagination = get_pagination(db=db, model=model,user_id=user_id, title=title, current=current, size=size,
                                status=status, is_deleted=is_deleted,
                                isAll=0
                                )
    return pagination.data

#获取总条数
def getTotal(db:Session,model=None,user_id:int=None,title:str="",status:int=0, is_deleted:int=0,isAll=0)->int:
    pagination = get_pagination(db=db,isAll=0, model=model, user_id=user_id,title=title,  status=status, is_deleted=is_deleted)
    return pagination.total