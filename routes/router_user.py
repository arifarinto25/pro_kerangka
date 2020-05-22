from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date
import logging
import random
import string

from .model_user import UserBase, UserOnDb, TokenData

router_user = APIRouter()

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

@router_user.post("/user", response_model=UserOnDb)
async def add_user(user: UserBase):
    user.createTime = datetime.utcnow()
    user.updateTime = datetime.utcnow()
    user.nama = user.nama.upper()
    user.hobi = user.hobi.upper()
    user_op = await DB.tbl_user.insert_one(user.dict())
    if user_op.inserted_id:
        user = await _get_user_or_404(user_op.inserted_id)
        return user


@router_user.get("/user", response_model=List[UserOnDb])
async def get_all_users(nama: str = '', hobi: str = '', size: int = 10, page: int = 0):
    skip = page * size
    criteria = []
    if len(nama) > 2:
        criteria.append({"nama": {'$regex': nama.upper()}})
    if len(hobi) > 2:
        criteria.append({"hobi" : {'$regex': hobi.upper(),"$options": "i"}})
    
    criteria = { "$and" : criteria } if len(criteria) > 0 else {}
    print(criteria)
    users_cursor = DB.tbl_user.find(criteria).skip(skip).limit(size)
    users = await users_cursor.to_list(length=size)
    return list(map(fix_id, users))


@router_user.get("/user/{id_}", response_model=UserOnDb)
async def get_user(id_: ObjectId = Depends(validate_object_id)):
    user = await DB.tbl_user.find_one({"_id": id_})
    if user:
        user = fix_id(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router_user.delete("/user/{id_}", dependencies=[Depends(_get_user_or_404)], response_model=dict)
async def delete_user(id_: ObjectId = Depends(validate_object_id)):
    user_op = await DB.tbl_user.delete_one({"_id": id_})
    if user_op.deleted_count:
        return {"status": f"deleted count: {user_op.deleted_count}"}


@router_user.put("/user/{id_}", response_model=UserOnDb)
async def update_user(user_data: UserBase, id_: ObjectId = Depends(validate_object_id)):
    user = await DB.tbl_user.find_one({"_id": id_})
    if user:
        user_data.updateTime = datetime.utcnow()
        user_data.createTime = user["createTime"]
        user_op = await DB.tbl_user.update_one(
            {"_id": id_}, {"$set": user_data.dict()}
        )
        if user_op.modified_count:
            return await _get_user_or_404(id_)
        else:
            raise HTTPException(status_code=304)
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router_user.get("/user_my_profile", response_model=UserOnDb)
async def get_user_my_profile(current_user: TokenData = Depends(get_current_user)):
    user = await DB.tbl_user.find_one({"_id": current_user.account})
    if user:
        user = fix_id(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")