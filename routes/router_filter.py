from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date
import logging
import random
import string

from .model_user import UserBase, UserOnDb, Gender, Hobby

router_filter = APIRouter()

def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id

async def _get_user_or_404(id_: str):
    _id = validate_object_id(id_)
    user = await DB.tbl_user.find_one({"_id": _id})
    if user:
        return fix_id(user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

def fix_id(user):
    user["id_"] = str(user["_id"])
    return user

def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

# =================================================================================

@router_filter.get("/user_jenis_kelamin", response_model=list)
async def get_user_jenis_kelamin():
    return list(Gender)

@router_filter.get("/user_hobi", response_model=list)
async def get_user_hobi():
    return list(Hobby)

@router_filter.get("/auto_search_user/{key}", response_model=List[UserOnDb])
async def auto_search_user(key: str, size: int = 10, page: int = 0):
    if len(key) >= 3:
        skip = page * size
        users_cursor = DB.tbl_user.find({"nama": {'$regex': key.upper()}}).skip(skip).limit(size)
        users = await users_cursor.to_list(length=size)
        return list(map(fix_id, users))
    else:
        return []