import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field 

class TopographyData(BaseModel):
    data: Dict[str, Any] ={
        "slope":"slope",
        "aspect":"aspect",
        "altitude":"altitude",
        "topography_type":"topography_type",
        "ground_area_coverage_km2":"ground_area_coverage_km2",
        "data_source":"data_source"
    }
    geographic_id: str = Field(..., alias="geographic_id")