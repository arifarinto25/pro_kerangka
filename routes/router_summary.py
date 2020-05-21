from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date, timedelta
import logging
import random
import string

from .model_user import UserBase, UserOnDb, Gender, Hobby
from .router_graph import get_user_pie_chart_jenis_kelamin, get_user_garis_chart_new_user_15_hari

router_summary = APIRouter()

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

@router_summary.get("/summary_user", response_model=dict)
async def get_summary():
    total = await DB.tbl_user.count_documents({})
    laki = await DB.tbl_user.count_documents({"jenisKelamin":"laki-laki"})
    perempuan = await DB.tbl_user.count_documents({"jenisKelamin":"perempuan"})
    start_date = datetime.utcnow() - timedelta(14)
    print(start_date)
    newUser = await DB.tbl_user.count_documents({
        "createTime": {"$gte": start_date}
    })
    return {
        "totalUser":total,
        "laki-laki":laki,
        "perempuan":perempuan,
        "newUser":newUser
    }

@router_summary.get("/dashboard", response_model=dict)
async def get_dashboard():
    data = await get_summary()
    graph1 = await get_user_pie_chart_jenis_kelamin()
    graph2 = await get_user_garis_chart_new_user_15_hari()
    return {"summary":data,"graph1":graph1,"graph2":graph2}