from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Gender(str,Enum):
    laki = "laki-laki"
    perempuan = "perempuan"

class Hobby(BaseModel):
    hobi: str = None

class HobbyOnDb(Hobby):
    id_: str

class UserBase(BaseModel):
    createTime: datetime = None
    updateTime: datetime = None
    nama: str = None
    image: str = None
    tglLahir: str = None
    jenisKelamin: Gender = None
    hobi: Hobby = None

class UserOnDb(UserBase):
    id_ : str
