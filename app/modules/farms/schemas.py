import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CropStage(str, Enum):
    """Catálogo cerrado, Ilustrativo hasta validar con fuente agronómica (dominio.md regla 13)."""

    RECIEN_PLANTADA = "recien_plantada"
    CRECIMIENTO = "crecimiento"
    FLORACION = "floracion"
    FRUTO = "fruto"
    COSECHA = "cosecha"


class FarmCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    region: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    area_hectares: float = Field(gt=0)
    soil_texture: str | None = Field(default=None, max_length=100)
    drainage: str | None = Field(default=None, max_length=100)
    organic_matter_percent: float | None = Field(default=None, ge=0, le=100)
    has_irrigation: bool = False


class FarmUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    region: str | None = Field(default=None, min_length=1, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    area_hectares: float | None = Field(default=None, gt=0)
    soil_texture: str | None = Field(default=None, max_length=100)
    drainage: str | None = Field(default=None, max_length=100)
    organic_matter_percent: float | None = Field(default=None, ge=0, le=100)
    has_irrigation: bool | None = None


class FarmResponse(BaseModel):
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
    created_at: datetime


class CropHistoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    crop: str = Field(min_length=1, max_length=100)
    planting_date: date
    stage: CropStage = CropStage.RECIEN_PLANTADA


class CropStageUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: CropStage


class CropHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    crop: str
    planting_date: date
    stage: str
    current: bool
    created_at: datetime
