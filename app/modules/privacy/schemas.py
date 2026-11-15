import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.modules.auth.schemas import UserProfileResponse

PROMOTIONAL_COMMS_KIND = "comunicaciones_promocionales"


class CropHistoryExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    crop: str
    planting_date: date
    stage: str
    current: bool
    created_at: datetime


class AlertExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    severity: str
    title: str
    expected_date: date | None
    active: bool
    created_at: datetime


class FarmExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    region: str
    latitude: float
    longitude: float
    area_hectares: float
    soil_texture: str | None
    drainage: str | None
    organic_matter_percent: float | None
    has_irrigation: bool
    crop_history: list[CropHistoryExport]
    alerts: list[AlertExport]


class MerchantProfileExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    business_name: str
    region: str
    products_of_interest: str
    contact: str | None
    updated_at: datetime


class SurplusExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: str
    kilos: float
    price: int
    region: str
    use: str
    status: str
    contact_visible: bool
    contact: str | None
    created_at: datetime


class PaymentExport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan: str
    amount: int
    currency: str
    status: str
    provider: str
    created_at: datetime


class ConsentExport(BaseModel):
    kind: str
    granted: bool
    version: str
    updated_at: datetime | None


class ConsentsResponse(BaseModel):
    comunicaciones_promocionales: ConsentExport


class ConsentsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comunicaciones_promocionales: bool


class DataExportResponse(BaseModel):
    exported_at: datetime
    account: UserProfileResponse
    farms: list[FarmExport]
    merchant_profile: MerchantProfileExport | None
    surplus: list[SurplusExport]
    payments: list[PaymentExport]
    consents: ConsentsResponse
