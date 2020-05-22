from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WizardEntity(BaseModel):
    var: str = None
    value: str = None

class WizardStep(BaseModel):
    id_: str = None
    stepNumber: int
    createTime: datetime = None
    updateTime: datetime = None
    stepName: str = None
    entity: List[WizardEntity] = []

class TipeId(str,Enum):
    uid = "uid"
    email = "email"
    phone = "phone"
    hardware = "hardware"

class WizardBase(BaseModel):
    createTime: datetime = None
    updateTime: datetime = None
    idCreatorTipe : TipeId = None
    idCreator: str = None
    idCustomerTipe: TipeId
    idCustomer: str
    nameCustomer: str = None
    wizName: str = None
    wizard: List[WizardStep] = []
    status: bool = False

class WizardOnDb(WizardBase):
    id_: str 
