from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException, Response, File, UploadFile
from typing import List
from datetime import datetime, date, timedelta
import pandas as pd
import logging
import random
import string
from io import BytesIO

from .model_user import UserBase, UserOnDb, Gender

router_action = APIRouter()

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

@router_action.get("/download_user.xls") #action download excel
async def download_user(size: int):
    skip = 0 * size
    users_cursor = DB.tbl_user.find().skip(skip).limit(size)
    users = await users_cursor.to_list(length=size)
    df =  pd.DataFrame(list(users))
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='data_user')
        writer.save()
        return Response(content=b.getvalue(), media_type='application/vnd.ms-excel')

@router_action.post("/upload_user") #upload data user dari excel
async def upload_user(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)
    print(df)
    result = []
    user = UserBase()
    for index,row in df.iterrows():
        user.createTime = datetime.utcnow()
        user.updateTime = datetime.utcnow()
        user.nama = row['nama'].upper()
        user.nohp = row['nohp']
        user.email = row['email']
        user.username = row['username']
        user.password = row['password']
        user.role = [row['role']]
        user.tempatLahir = row['tempatLahir']
        user.tglLahir = row['tglLahir']
        user.jenisKelamin = row['jenisKelamin']
        user.alamat = row['alamat']
        user.hobi = row['hobi']
        user.image = row['image']
        result.append(user.dict())
    #aneh
    print(result)
    DB.tbl_user.insert_many(result)
    return {"ok"}