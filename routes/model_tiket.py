# backend/tancho/tickets/models.py

from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ColourType(str, Enum):
    green = "Green"
    yellow = "Yellow"
    orange = "Orang"
    red = "Red"

class ComplainType(str, Enum):
    unknown = "Unknown"
    mobile = "Mobile"
    web = "Web"
    master = "Account"
    finance = "Finance"
    academic = "Academic"

class CustomerType(str, Enum):
    reg = "Registered"
    unreg = "Unregistered"

class CustomerChannel(str, Enum):
    mobile = "Mobile"
    web = "Web"

class Message(BaseModel):
    firebase: Optional[str] = None #firebase
    writerName: Optional[str] = None
    message: Optional[str] = None
    readStatus: bool = False
    isDelete: bool = False
    dateTime: datetime = datetime.now()

class TicketBase(BaseModel):
    lastTime: datetime = datetime.now()
    lastMsg: Optional[str] = None
    lastSender: Optional[str] = None
    ticketStatus: bool = True
    complainType: ComplainType = "Unknown"
    colourType: ColourType = "Green"
    csId: Optional[str] = None
    csName: Optional[str] = None
    csFirebase: Optional[str] = None
    csType: Optional[str] = None
    customerType: Optional[CustomerType]
    customerFirebase: Optional[str] = None
    companyCode: Optional[str] = None
    companyName: Optional[str] = None
    customerId: Optional[str] = None
    customerName: Optional[str] = None
    customerChannel: CustomerChannel = None
    message: List[Message] = []

class TicketOnDB(TicketBase):
    id_: str
    