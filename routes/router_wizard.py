#TODO input mode wizard
from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date
import logging
import random
import string

from .model_user import Hobby, HobbyOnDb

router_wizard = APIRouter()

def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id

async def _get_wizard_or_404(id_: str):
    _id = validate_object_id(id_)
    wizard = await DB.tbl_wizard.find_one({"_id": _id})
    if wizard:
        return fix_id(wizard)
    else:
        raise HTTPException(status_code=404, detail="Wizard not found")

def fix_id(wizard):
    wizard["id_"] = str(wizard["_id"])
    return wizard

def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

# =================================================================================

@router_wizard.post("/wizard", response_model=HobbyOnDb)
async def add_wizard(wizard: Hobby):
    wizard.wizard = wizard.wizard.upper()
    wizard_op = await DB.tbl_wizard.insert_one(wizard.dict())
    if wizard_op.inserted_id:
        wizard = await _get_wizard_or_404(wizard_op.inserted_id)
        return wizard


@router_wizard.get("/wizard", response_model=List[HobbyOnDb])
async def get_all_wizards(size: int = 10, page: int = 0):
    skip = page * size
    wizards_cursor = DB.tbl_wizard.find().skip(skip).limit(size)
    wizards = await wizards_cursor.to_list(length=size)
    return list(map(fix_id, wizards))


@router_wizard.get("/wizard/{id_}", response_model=HobbyOnDb)
async def get_wizard(id_: ObjectId = Depends(validate_object_id)):
    wizard = await DB.tbl_wizard.find_one({"_id": id_})
    if wizard:
        wizard = fix_id(wizard)
        return wizard
    else:
        raise HTTPException(status_code=404, detail="Wizard not found")


@router_wizard.delete("/wizard/{id_}", dependencies=[Depends(_get_wizard_or_404)], response_model=dict)
async def delete_wizard(id_: ObjectId = Depends(validate_object_id)):
    wizard_op = await DB.tbl_wizard.delete_one({"_id": id_})
    if wizard_op.deleted_count:
        return {"status": f"deleted count: {wizard_op.deleted_count}"}


@router_wizard.put("/wizard/{id_}", response_model=HobbyOnDb)
async def update_wizard(wizard_data: Hobby, id_: ObjectId = Depends(validate_object_id)):
    wizard = await DB.tbl_wizard.find_one({"_id": id_})
    if wizard:
        wizard_op = await DB.tbl_wizard.update_one(
            {"_id": id_}, {"$set": wizard_data.dict()}
        )
        if wizard_op.modified_count:
            return await _get_wizard_or_404(id_)
        else:
            raise HTTPException(status_code=304)
    else:
        raise HTTPException(status_code=404, detail="Wizard not found")