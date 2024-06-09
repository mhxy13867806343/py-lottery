from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
class SignatureOutput(BaseModel):
    id: Optional[int]=None
class SignatureInput(BaseModel):
    content: Optional[str]=None

