from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast

class AccountInput(BaseModel):
    account: str
    password: str
    type:Optional[int] = 0 #0管理员 1用户
class PhoneInput(BaseModel):
    phone: str
class UserInput(BaseModel):
    name: str
    phone: str
class UserQcInput(PhoneInput):
    name: Optional[str] = None
    account: str
class LotteryInput(UserInput):
    last_time: int
