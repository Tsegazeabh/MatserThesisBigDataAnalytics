from typing import Any, Dict
from pydantic import BaseModel, Field

class VIData(BaseModel):
    data: Dict[str, Any] ={
                            "NDVI": 0.56,
                            "EVI": 0.90,
                            "NDWI":0.42,
                            "SAVI": 0.30
                          }
    geographic_id: str = Field(..., alias="geographic_id")
