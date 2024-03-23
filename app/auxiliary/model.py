from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union, TypeVar, Type, Callable, cast
class AuxiliaryInput(BaseModel):
    email: str
class AuxiliaryInputFirst(AuxiliaryInput):
    title: Optional[str] = None
    content: str