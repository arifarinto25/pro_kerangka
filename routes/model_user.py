from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .model_image import ImageBase

class RoleType(str, Enum):
    admin = "admin"
    user = "user"
    customer = "customer"

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
    nohp: str = None
    email: str = None
    username: str = None
    password: str = None
    role: List[RoleType] = []
    tempatLahir: str = None
    tglLahir: str = None
    jenisKelamin: Gender = None
    alamat: str = None
    hobi: str = None
    image: ImageBase = None

class UserOnDb(UserBase):
    id_ : str

#TODO token 
class TokenData(BaseModel):
    sub: str #nama user
    account: str #account uid
    authorities: List[str] = [] #role
    company: str = "" #company uid
    code: str = "" #company code
    name: str = "" #nama company
    exp: int = 600

class Token(BaseModel):
    access_token: str
    token_type: str