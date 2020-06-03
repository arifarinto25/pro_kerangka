from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date
import logging
import random
import string

from .model_product import CategoryBase, CategoryOnDb

router_category = APIRouter()

def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id

async def _get_category_or_404(id_: str):
    _id = validate_object_id(id_)
    category = await DB.tbl_category.find_one({"_id": _id})
    if category:
        return fix_id(category)
    else:
        raise HTTPException(status_code=404, detail="Category not found")

def fix_id(category):
    category["id_"] = str(category["_id"])
    return category

def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

# =================================================================================

@router_category.post("/category", response_model=CategoryOnDb)
async def add_category(category: CategoryBase):
    category.createTime = datetime.utcnow()
    category.updateTime = datetime.utcnow()
    category.category = category.category.upper()
    category_op = await DB.tbl_category.insert_one(category.dict())
    if category_op.inserted_id:
        category = await _get_category_or_404(category_op.inserted_id)
        return category


@router_category.get("/category", response_model=List[CategoryOnDb])
async def get_all_categorys(category: str = '', size: int = 10, page: int = 0):
    skip = page * size
    criteria = []
    if len(category) > 2:
        criteria.append({"category": {'$regex': category.upper()}})
    
    criteria = { "$and" : criteria } if len(criteria) > 0 else {}
    print(criteria)
    categorys_cursor = DB.tbl_category.find(criteria).skip(skip).limit(size)
    categorys = await categorys_cursor.to_list(length=size)
    return list(map(fix_id, categorys))


@router_category.get("/category/{id_}", response_model=CategoryOnDb)
async def get_category(id_: ObjectId = Depends(validate_object_id)):
    category = await DB.tbl_category.find_one({"_id": id_})
    if category:
        category = fix_id(category)
        return category
    else:
        raise HTTPException(status_code=404, detail="Category not found")


@router_category.delete("/category/{id_}", dependencies=[Depends(_get_category_or_404)], response_model=dict)
async def delete_category(id_: ObjectId = Depends(validate_object_id)):
    category_op = await DB.tbl_category.delete_one({"_id": id_})
    if category_op.deleted_count:
        return {"status": f"deleted count: {category_op.deleted_count}"}


@router_category.put("/category/{id_}", response_model=CategoryOnDb)
async def update_category(category_data:dict , id_: ObjectId = Depends(validate_object_id)):
    category = await DB.tbl_category.find_one({"_id": id_})
    if category:
        category_data["updateTime"] = datetime.utcnow()
        category_op = await DB.tbl_category.update_one(
            {"_id": id_}, {"$set": category_data}
        )
        if category_op.modified_count:
            return await _get_category_or_404(id_)
        else:
            raise HTTPException(status_code=304)
    else:
        raise HTTPException(status_code=404, detail="Category not found")
