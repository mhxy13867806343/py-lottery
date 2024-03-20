from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
def getPistPagenaTion(db:Session,dbms=None,current:int=1,size:int=20)->Optional[List[Dict[str, Any]]]:
    offsetCurrent=(current-1)*size
    array=db.query(dbms).offset(offsetCurrent).limit(size).all()
    return array

#获取总条数
def getPistPagenationTotal(db:Session,dbms=None)->int:
    count=db.query(dbms).count()
    return count