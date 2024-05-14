from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from models.geographic_data import GeographicData

class SoilData(BaseModel):
    soil_name:str
    soil_type:str
    soil_pH:Optional[float]
    soil_CEC:Optional[float]
    soil_salinity:Optional[float]
    soil_bulk_density:Optional[float]
    soil_OC:Optional[float]
    soil_clay:Optional[float]
    soil_phosphorus:Optional[float]
    soil_potassium:Optional[float]
    soil_temperature: Optional[float]
    soil_moisture:Optional[float]
    soil_electrical_conductivity:Optional[float]
    geographic_id: GeographicData = Field(..., alias="geographic_id")
