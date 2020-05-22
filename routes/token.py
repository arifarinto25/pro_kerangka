from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from passlib.context import CryptContext

from .model_user import TokenData, Token
from config.config import DB, CONF

SECRET_KEY = "s47r5k0h4oi4d2j"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/katalispy/token/token")

router_token = APIRouter()


@router_token.post("/token", response_model=Token)
async def login_for_access_token( form_data: OAuth2PasswordRequestForm = Depends()):
    user = await DB.tbl_user.find_one({"username": form_data.username, "password": form_data.password})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data_token = TokenData()
    data_token.sub = user["nama"]
    data_token.account = user["userId"]
    data_token.authorities = user["role"]
    data_token.company = user["companyId"]
    data_token.code = user["companyCode"]
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data_token, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def create_access_token(data: TokenData, expires_delta: timedelta = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    data.exp = expire
    encoded_jwt = jwt.encode(data.dict(), SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        account: str = payload.get("account")
        authorities : str = payload.get("authorities")
        company : str = payload.get("company")
        code : str = payload.get("code")
        name : str = payload.get("name")
        exp : int = payload.get("exp")
        if sub is None:
            raise credentials_exception
        token_data = TokenData(sub=sub,account=account,authorities=authorities,company=company,code=code,name=name,exp=exp)
    except PyJWTError:
        raise credentials_exception
    return token_data