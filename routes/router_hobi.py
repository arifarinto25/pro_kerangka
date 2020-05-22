from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date
import logging
import random
import string

from .model_user import Hobby, HobbyOnDb

router_hobi = APIRouter()

def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id

async def _get_hobi_or_404(id_: str):
    _id = validate_object_id(id_)
    hobi = await DB.tbl_hobi.find_one({"_id": _id})
    if hobi:
        return fix_id(hobi)
    else:
        raise HTTPException(status_code=404, detail="Hobi not found")

def fix_id(hobi):
    hobi["id_"] = str(hobi["_id"])
    return hobi

def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

# =================================================================================

@router_hobi.post("/hobi", response_model=HobbyOnDb)
async def add_hobi(hobi: Hobby):
    hobi.hobi = hobi.hobi.upper()
    hobi_op = await DB.tbl_hobi.insert_one(hobi.dict())
    if hobi_op.inserted_id:
        hobi = await _get_hobi_or_404(hobi_op.inserted_id)
        return hobi


@router_hobi.get("/hobi", response_model=List[HobbyOnDb])
async def get_all_hobis(size: int = 10, page: int = 0):
    skip = page * size
    hobis_cursor = DB.tbl_hobi.find().skip(skip).limit(size)
    hobis = await hobis_cursor.to_list(length=size)
    return list(map(fix_id, hobis))


@router_hobi.get("/hobi/{id_}", response_model=HobbyOnDb)
async def get_hobi(id_: ObjectId = Depends(validate_object_id)):
    hobi = await DB.tbl_hobi.find_one({"_id": id_})
    if hobi:
        hobi = fix_id(hobi)
        return hobi
    else:
        raise HTTPException(status_code=404, detail="Hobi not found")


@router_hobi.delete("/hobi/{id_}", dependencies=[Depends(_get_hobi_or_404)], response_model=dict)
async def delete_hobi(id_: ObjectId = Depends(validate_object_id)):
    hobi_op = await DB.tbl_hobi.delete_one({"_id": id_})
    if hobi_op.deleted_count:
        return {"status": f"deleted count: {hobi_op.deleted_count}"}


@router_hobi.put("/hobi/{id_}", response_model=HobbyOnDb)
async def update_hobi(hobi_data:dict, id_: ObjectId = Depends(validate_object_id)):
    hobi = await DB.tbl_hobi.find_one({"_id": id_})
    if hobi:
        hobi_op = await DB.tbl_hobi.update_one(
            {"_id": id_}, {"$set": hobi_data}
        )
        if hobi_op.modified_count:
            return await _get_hobi_or_404(id_)
        else:
            raise HTTPException(status_code=304)
    else:
        raise HTTPException(status_code=404, detail="Hobi not found")