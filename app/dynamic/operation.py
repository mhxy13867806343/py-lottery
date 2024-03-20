from sqlalchemy.orm import Session
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

def get_pagination(db: Session, model: Type[T], title: Optional[str] = "", status: Optional[int] = 0, current: int = 1, size: int = 20) -> Pagination[T]:
    base_query = db.query(model)
    if title:
        base_query = base_query.filter(model.title.like(f"%{title}%"))
    if status is not None:
        base_query = base_query.filter(model.status == status)
    total = base_query.count()

    _sum = (current - 1) * size
    items = base_query.offset(_sum).limit(size).all()

    return Pagination[T](
        data=items,
        total=total,
        current=current,
        size=size
    )

def getPagenation(db:Session,model=None,title:str="",current:int=1,size:int=20)->[UserPosts]:
    pagination = get_pagination(db=db, model=model, title=title, current=current, size=size)
    return pagination.data

#获取总条数
def getTotal(db:Session,model=None,title:str="")->int:
    pagination = get_pagination(db=db, model=model, title=title)
    return pagination.total