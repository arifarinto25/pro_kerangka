from bson import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, date, timedelta
import logging
import random
import string

from .model_user import UserBase, UserOnDb, Gender, Hobby

router_graph = APIRouter()


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


@router_graph.get("/user_pie_chart_jenis_kelamin", response_model=dict)
async def get_user_pie_chart_jenis_kelamin():
    total = await DB.tbl_user.count_documents({})
    laki = await DB.tbl_user.count_documents({"jenisKelamin": "laki-laki"})
    perempuan = await DB.tbl_user.count_documents({"jenisKelamin": "perempuan"})
    return {
        "labels": ["laki-laki", "perempuan"],
        "datasets": [{
            "data": [laki, perempuan],
            "backgroundColor": ["#FF6384", "#36A2EB"],
            "hoverBackgroundColor":["#FF6384", "#36A2EB"]
        }]
    }


@router_graph.get("/user_garis_chart_new_user_15_hari", response_model=dict)
async def get_user_garis_chart_new_user_15_hari():
    total = await DB.tbl_user.count_documents({})
    start_date = datetime.utcnow() - timedelta(14)
    print(start_date)
    newUser = await DB.tbl_user.count_documents({
        "createTime": {"$gte": start_date}
    })
    pipeline = [
        {"$match": {"createTime": {"$gte": start_date}}},
        {
            "$group":
            {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$createTime"}},
                # "totalAmount": {"$sum": "$qty"},
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    favorit_cursor = DB.tbl_user.aggregate(pipeline)
    favorit = await favorit_cursor.to_list(15)
    labels = []
    datas = []
    y = 0
    for x in range(15):
        if favorit[y]["_id"] == start_date.strftime('%Y-%m-%d'):
            labels.append(favorit[y]["_id"])
            datas.append(favorit[y]["count"])
            y += 1
        else:
            labels.append(start_date.strftime('%Y-%m-%d'))
            datas.append(0)
        start_date += timedelta(1)

    return {
        "labels": labels,
        "datasets": [
            {
                "label": 'New User',
                "fill": True,
                "lineTension": 0.1,
                "backgroundColor": 'rgba(75,192,192,0.4)',
                "borderColor": 'rgba(75,192,192,1)',
                "pointHitRadius": 10,
                "data": datas,
            }
        ]
    }
