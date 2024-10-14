from pydantic import BaseModel
from typing import Optional, List, Union


class chatPayloadModel(BaseModel):
    model: Optional[str] = None
    pathName: Optional[str] = None
    prompt: Optional[Union[str, List[str]]] = None
    dataType: Optional[str] = None

class referPayloadModel(BaseModel):
    category: Optional[str] = None
    prompt: Optional[str] = None