from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date
import logging
import random
import string

from .model_product import ProductBase, ProductOnDb

router_product = APIRouter()

def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id

async def _get_product_or_404(id_: str):
    _id = validate_object_id(id_)
    product = await DB.tbl_product.find_one({"_id": _id})
    if product:
        return fix_id(product)
    else:
        raise HTTPException(status_code=404, detail="Product not found")

def fix_id(product):
    product["id_"] = str(product["_id"])
    return product

def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

# =================================================================================

@router_product.post("/product", response_model=ProductOnDb)
async def add_product(product: ProductBase):
    product.createTime = datetime.utcnow()
    product.updateTime = datetime.utcnow()
    product.name = product.name.upper()
    product.category = product.category.upper()
    product_op = await DB.tbl_product.insert_one(product.dict())
    if product_op.inserted_id:
        product = await _get_product_or_404(product_op.inserted_id)
        return product


@router_product.get("/product", response_model=List[ProductOnDb])
async def get_all_products(name: str = '', category: str = '', size: int = 10, page: int = 0):
    skip = page * size
    criteria = []
    if len(name) > 2:
        criteria.append({"name": {'$regex': name.upper()}})
    if len(category) > 2:
        criteria.append({"category" : {'$regex': category.upper(),"$options": "i"}})
    
    criteria = { "$and" : criteria } if len(criteria) > 0 else {}
    print(criteria)
    products_cursor = DB.tbl_product.find(criteria).skip(skip).limit(size)
    products = await products_cursor.to_list(length=size)
    return list(map(fix_id, products))


@router_product.get("/product/{id_}", response_model=ProductOnDb)
async def get_product(id_: ObjectId = Depends(validate_object_id)):
    product = await DB.tbl_product.find_one({"_id": id_})
    if product:
        product = fix_id(product)
        return product
    else:
        raise HTTPException(status_code=404, detail="Product not found")


@router_product.delete("/product/{id_}", dependencies=[Depends(_get_product_or_404)], response_model=dict)
async def delete_product(id_: ObjectId = Depends(validate_object_id)):
    product_op = await DB.tbl_product.delete_one({"_id": id_})
    if product_op.deleted_count:
        return {"status": f"deleted count: {product_op.deleted_count}"}


@router_product.put("/product/{id_}", response_model=ProductOnDb)
async def update_product(product_data:dict , id_: ObjectId = Depends(validate_object_id)):
    product = await DB.tbl_product.find_one({"_id": id_})
    if product:
        product_data["updateTime"] = datetime.utcnow()
        product_op = await DB.tbl_product.update_one(
            {"_id": id_}, {"$set": product_data}
        )
        if product_op.modified_count:
            return await _get_product_or_404(id_)
        else:
            raise HTTPException(status_code=304)
    else:
        raise HTTPException(status_code=404, detail="Product not found")
