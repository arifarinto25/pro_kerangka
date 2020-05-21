from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .model_image import ImageBase

class Gender(str,Enum):
    laki = "laki-laki"
    perempuan = "perempuan"

class Hobby(BaseModel):
    hobi: str = None

class HobbyOnDb(Hobby):
    id_: str

class UserBase(BaseModel): #TODO lengkapi data + fungsi token
    createTime: datetime = None
    updateTime: datetime = None
    nama: str = None
    nohp: str = None
    email: str = None
    username: str = None
    password: str = None
    tempatLahir: str = None
    tglLahir: str = None
    jenisKelamin: Gender = None
    alamat: str = None
    hobi: str = None
    image: ImageBase = None

class UserOnDb(UserBase):
    id_ : str
