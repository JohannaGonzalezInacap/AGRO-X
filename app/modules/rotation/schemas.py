import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PriorityDimension(str, Enum):
    WATER = "water"
    SOIL = "soil"
    INCOME = "income"


DEFAULT_PRIORITY_ORDER = [PriorityDimension.WATER, PriorityDimension.SOIL, PriorityDimension.INCOME]


class CropResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    family: str
    water_need: str
    nitrogen_effect: str
    root_depth: str
    frost_tolerance: str
    heat_tolerance: str
    illustrative: bool


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Orden de mayor a menor importancia. Por defecto: agua, suelo, ingreso.
    priorities: list[PriorityDimension] = Field(default_factory=lambda: list(DEFAULT_PRIORITY_ORDER))


class RecommendationItem(BaseModel):
    crop: str
    score: int
    reasons: list[str]
    illustrative: bool
    # El reto pide comparar "al menos tres estrategias de rotación, incluida la actual" — esta
    # marca cuál de los ítems es "quedarse con lo que ya tienes", no una rotación nueva.
    is_current: bool = False


class RecommendationResponse(BaseModel):
    items: list[RecommendationItem]
    sources_used: list[str]
    notices: list[str]
