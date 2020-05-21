#TODO input mode wizard
from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date
import logging
import random
import string

from .model_wizard import WizardBase, WizardOnDb, WizardStep, WizardStep1, WizardStep2

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
# step 1 : isi nama, nohp, email
# step 2 : isi tempat lahir, tanggal lahir, jenis kelamin, hobi
# step 3 : upload image
# step 4 : username, password

@router_wizard.post("/wizard_user_step1", response_model=WizardOnDb) #initiate wizard
async def wizard_user_step1(wizard: WizardStep1):
    sekarang = datetime.utcnow()
    wizard.createTime = sekarang
    wizard.updateTime = sekarang
    wizard.wizName = wizard.wizName.upper()
    wizard.wizard[0].id_ = randomString(6)
    wizard.wizard[0].stepNumber = 1
    wizard.wizard[0].createTime = sekarang
    wizard.wizard[0].updateTime = sekarang
    wizard_op = await DB.tbl_wizard.insert_one(wizard.dict())
    if wizard_op.inserted_id:
        wizard = await _get_wizard_or_404(wizard_op.inserted_id)
        return wizard

@router_wizard.post("/wizard_user_step2/{id_}", response_model=WizardStep) #push wizard array
async def wizard_user_step2(wizard: WizardStep2, id_: ObjectId = Depends(validate_object_id)):
    sekarang = datetime.utcnow()
    wizard_cek = await DB.tbl_wizard.find_one({"_id": id_})
    if wizard_cek:
        wizard.id_ = randomString(6)
        wizard.stepNumber = 2
        wizard.createTime = sekarang
        wizard.updateTime = sekarang
        wizard_op = await DB.tbl_wizard.update_one(
            {"_id":id_,"wizard.stepNumber":2},
            {"$set": {"wizard.$": wizard.dict(),"updateTime": sekarang}}
        )
        if wizard_op.modified_count:
            return wizard
        else:
            print("aneh")
            wizard_add = await DB.tbl_wizard.update_one(
                {"_id":id_},
                {"$addToSet": { "wizard": wizard.dict()},
                 "$set": {"updateTime": sekarang}}
            )
            return wizard
    else:
        raise HTTPException(status_code=404, detail="Wizard not found")

@router_wizard.get("/wizard", response_model=List[WizardOnDb])
async def get_all_wizards(size: int = 10, page: int = 0):
    skip = page * size
    wizards_cursor = DB.tbl_wizard.find().skip(skip).limit(size)
    wizards = await wizards_cursor.to_list(length=size)
    return list(map(fix_id, wizards))


@router_wizard.get("/wizard/{id_}", response_model=WizardOnDb)
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


@router_wizard.put("/wizard/{id_}", response_model=WizardOnDb)
async def update_wizard(wizard_data: WizardBase, id_: ObjectId = Depends(validate_object_id)):
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