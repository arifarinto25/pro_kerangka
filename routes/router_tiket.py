# backend/tancho/tickets/routes.py

from bson.objectid import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import logging

from .model_tiket import TicketBase, TicketOnDB, Message, CustomerChannel
from .model_user import TokenData
from .token import get_current_user

router_tiket = APIRouter()


def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id


async def _get_ticket_or_404(id_: str):
    _id = validate_object_id(id_)
    ticket = await DB.tbl_ticket.find_one({"_id": _id})
    if ticket:
        return fix_ticket_id(ticket)
    else:
        raise HTTPException(status_code=404, detail="Ticket not found")


def fix_ticket_id(ticket):
    ticket["id_"] = str(ticket["_id"])
    return ticket

# ==========================================================================================

#CREATE TIKET UNLOGIN
@router_tiket.post("/sendchat/unlogin/{channel}/{companyCode}", response_model=Message)
async def add_ticket_unlogin(channel: CustomerChannel, companyCode: str, msg: Message):
    msg.dateTime = datetime.utcnow()
    firebase = await DB.tbl_ticket.find_one({"customerFirebase": msg.firebase},{"_id":1})
    if firebase:
        ticket_op = await DB.tbl_ticket.update_one(
            { "customerFirebase": msg.firebase},
            { "$addToSet": { "message": msg.dict()}, 
            "$set": { "lastTime": msg.dateTime, "lastMsg": msg.message, "lastSender": "user"} 
            }
        )
        #TODO kirim firebase cs, jika ada
        return msg
    else:
        ticket = TicketBase()
        ticket.lastTime = datetime.utcnow()
        ticket.customerType = "Unregistered"
        ticket.companyCode = companyCode
        ticket.customerFirebase = msg.firebase
        ticket.customerChannel = channel
        ticket.message = [msg]
        ticket_op = await DB.tbl_ticket.insert_one(ticket.dict())
        return msg

#GET LIST CHAT BY FIREBASE ID
@router_tiket.get("/chatlist/{firebase}", response_model=TicketOnDB)
async def get_detail_chats_list_by_firebase(firebase: str):
    chats = await DB.tbl_ticket.find_one({"customerFirebase": firebase})
    if chats:
        chats["id_"] = str(chats["_id"])
        return chats
    else:
        raise HTTPException(status_code=404, detail="Chat not found")

#CREATE TIKET by LOGIN
@router_tiket.post("/sendchat/login/{channel}", response_model=Message)
async def add_ticket_by_login(channel: CustomerChannel, msg: Message, current_user: TokenData = Depends(get_current_user)):
    msg.dateTime = datetime.utcnow()
    firebase = await DB.tbl_ticket.find_one({"customerFirebase": msg.firebase, "companyCode": current_user.code},{"_id":1})
    if firebase:
        ticket_op = await DB.tbl_ticket.update_one(
            { "customerFirebase": msg.firebase},
            { "$addToSet": { "message": msg.dict()}, 
            "$set": { "lastTime": msg.dateTime, "lastMsg": msg.message, "lastSender": "user"} 
            }
        )
        #TODO kirim firebase cs, jika ada
        return msg
    else:
        ticket = TicketBase()
        ticket.lastTime = datetime.utcnow()
        ticket.lastMsg = msg.message
        ticket.lastSender = "user"
        ticket.customerType = "Registered"
        ticket.companyCode = current_user.code
        ticket.companyName = current_user.name
        ticket.customerName = current_user.sub
        ticket.customerId = current_user.account
        ticket.customerFirebase = msg.firebase
        ticket.customerChannel = channel
        ticket.message = [msg]
        ticket_op = await DB.tbl_ticket.insert_one(ticket.dict())
        return msg


#GET LIST TICKET BY ADMIN
@router_tiket.get("/chatlistadmin", response_model=List[TicketOnDB])
async def get_tickets_list_by_admin(size: int = 100, page: int = 0, current_user: TokenData = Depends(get_current_user)):
    skip = page * size
    if current_user.authorities[0] == "ROLE_SUPER_ADMIN":
        filter_company = {}
    else:
        filter_company = {"companyCode":current_user.code}
    tickets_cursor = DB.tbl_ticket.find(filter_company,{"message":0}).skip(skip).limit(size)
    tickets = await tickets_cursor.to_list(length=size)
    return list(map(fix_ticket_id, tickets))

#BALAS TIKET OLEH CS PUSAT YANG UDA LOGIN
@router_tiket.post("/sendchat/admin/{idticket}", response_model=Message)
async def respon_ticket(idticket: str, msg: Message, current_user: TokenData = Depends(get_current_user)):
    msg.writerName = current_user.sub + ' - ' + current_user.authorities[0]
    msg.dateTime = datetime.utcnow()
    firebase = await DB.tbl_ticket.find_one({"_id": ObjectId(idticket)},{"_id":1,"customerFirebase":1})
    if firebase:
        ticket_op = await DB.tbl_ticket.update_one(
            { "_id": ObjectId(idticket)},
            { "$addToSet": { "message": msg.dict()}, 
            "$set": { "lastTime": msg.dateTime, "lastMsg": msg.message, "lastSender": "cs",
            "csName": current_user.sub, "csType": current_user.authorities[0], 
            "csId": current_user.account, "csFirebase": msg.firebase} 
            }
        )
        #TODO kirim firebase customer
        return msg
    else:
        return HTTPException(status_code=404, detail="Ticket ID not found")