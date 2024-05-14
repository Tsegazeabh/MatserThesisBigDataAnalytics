import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field 
from models.geographic_data import GeographicData

class TopographyData(BaseModel):
    slope: float
    aspect: str
    altitude:float
    topography_type: str
    ground_area_coverage_km2: float
    data_source: Optional[str]
    geographic_id: GeographicData = Field(..., alias="geographic_id")