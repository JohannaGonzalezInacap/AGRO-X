import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SurplusStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"


class MerchantProfileUpsert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business_name: str = Field(min_length=1, max_length=255)
    region: str = Field(min_length=1, max_length=255)
    products_of_interest: str = ""
    contact: str | None = None


class MerchantProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    business_name: str
    region: str
    products_of_interest: str
    contact: str | None
    updated_at: datetime


class SurplusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: str = Field(min_length=1, max_length=100)
    kilos: float = Field(gt=0)
    price: int = Field(ge=0)
    region: str = Field(min_length=1, max_length=255)
    use: str = Field(min_length=1, max_length=100)
    contact_visible: bool = False
    contact: str | None = None


class SurplusStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: SurplusStatus


class SurplusResponse(BaseModel):
    id: uuid.UUID
    product: str
    kilos: float
    price: int
    region: str
    use: str
    status: str
    contact: str | None
    created_at: datetime
