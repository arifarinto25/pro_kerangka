from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ImageType(str, Enum):
    std = "std"
    thumb = "thumb"
    ico = "ico"

class ImageBase(BaseModel):
    name: str = None

class MediaBase(ImageBase):
    createTime: Optional[datetime] = None
    updateTime: Optional[datetime] = None
    companyId: str = None
    creatorId: str = None
    file_type: str = None
    used: int = 0
    temp: bool = True
    origin_name: str = None
    file_name: str = None #20_05_20_100x100_abcdefgh_ico/thumb/std

class MediaBaseOnDb(MediaBase):
    _id: str