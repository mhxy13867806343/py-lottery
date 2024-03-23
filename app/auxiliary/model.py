from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
class AuxiliaryInput(BaseModel):
    email: str
class AuxiliaryInputFirst(AuxiliaryInput):
    title: Optional[str] = None
    content: str
class AuxiliaryInputPostNunSize(AuxiliaryInput):
    pageNum: Optional[int] = 1
    pageSize: Optional[int] = 10
class AuxiliaryCopyInput(AuxiliaryInputFirst):
    id: int