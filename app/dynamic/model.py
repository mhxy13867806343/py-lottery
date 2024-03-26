from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
class AccountInputFirst(BaseModel):
    name: Optional[str] = None
class DynamicInput(AccountInputFirst):
    content: str
    id: Optional[str] = None
    type: Optional[int] = 0
class DynamicUserShare(BaseModel):
    share_type: int  #0:复制链接 1:二维码
    dynamic_id:int #动态id