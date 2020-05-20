from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WizardEntity(BaseModel):
    var: str = None
    value: str = None

class WizardStep(BaseModel):
    id_: str = None
    number: int = 0
    createTime: datetime = None
    updateTime: datetime = None
    name: str = None
    entity: List[WizardEntity] = []

class WizardBase(BaseModel):
    idCreator: str = None
    idCustomer: str = None #email, idAccount, idCustomer, idUser
    wizard: List[WizardStep] = []

class WizardOnDb(WizardBase):
    id_: str 

