from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast

class AccountInputFirst(BaseModel):
    name: Optional[str] = None
class AccountInputEamail(BaseModel):
    email: Optional[str] = None

class AccountInputEamail1(AccountInputEamail):
    code: Optional[str] = None