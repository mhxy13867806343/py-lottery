from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
class AccountInputFirst(BaseModel):
    name: Optional[str] = None
class DynamicInput(AccountInputFirst):
    content: str
    id: Optional[str] = None
    type: Optional[int] = 0 #0:公开 1:私有