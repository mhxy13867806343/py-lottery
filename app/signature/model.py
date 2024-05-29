from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
class SignatureFirst(BaseModel):
    content: Optional[str] = None
    id:Optional[str]=None