from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from models.geographic_data import GeographicData

class VIData(BaseModel):
    NDVI:str
    DVI:str
    EVI:Optional[float]
    NDWI:Optional[float]
    MSAVI:Optional[float]
    TVI:Optional[float]
    geographic_id: GeographicData = Field(..., alias="geographic_id")
