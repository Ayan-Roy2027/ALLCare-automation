from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LeadStatus(str,Enum):
    NEW = 'new'
    BOT_ENGAGED = 'bot_engaged'
    HUMAN_ASSIGNED = 'human_assigned'
    CLOSED = 'closed'

class OptInStatus(str,Enum):
    NOT_CONTACTED = 'not_contacted'
    OPT_IN_SENT = "opt_in_sent"
    OPTED_IN = 'opted_in'
    OPTED_OUT = 'opted_out'

class Lead(BaseModel):
    lead_id : Optional[int] = None
    phone : str
    name : Optional[str] = None
    category : Optional[str] = None
    requirement : Optional[str] = None
    location : Optional[str] = None
    status : LeadStatus = LeadStatus.NEW
    created_at : datetime = Field(default_factory= datetime.now)

class OptInRecord(BaseModel):
    phone: str
    status: OptInStatus = OptInStatus.NOT_CONTACTED
    last_updated: datetime = Field(default_factory=datetime.now)

class Contact(BaseModel):
    phone : str
    name : Optional[str] = None
