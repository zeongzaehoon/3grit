from pydantic import BaseModel, Field
from typing import Optional



class RegisterStoreBody(BaseModel):
    CategoryId: int | None = Field(default=None, gt=0)
    SubCategoryId: int | None = Field(default=None, gt=0)
    
    Name: str = Field(min_length=2, max_length=32)
    MapX: float = Field(ge=-180, le=180)
    MapY: float = Field(ge=-90, le=90)
    AddressName: str = Field(min_length=2, max_length=100)
    KakaoMapId: int = Field(gt=0)
    