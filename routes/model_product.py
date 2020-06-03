from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CategoryBase(BaseModel):
    createTime: datetime = None
    updateTime: datetime = None
    category: str = None
    subTitle: str = None
    image: str = None

class CategoryOnDb(CategoryBase):
    id_: str

class ProductBase(BaseModel):
    createTime: datetime = None
    updateTime: datetime = None
    name: str = None
    subTitle: str = None
    descText: str = None
    descList: List[str] = []
    category: str = None
    priceNormal: int = 0
    priceFinal: int = 0
    image: str = None
    status: bool = True

class ProductOnDb(ProductBase):
    id_ : str