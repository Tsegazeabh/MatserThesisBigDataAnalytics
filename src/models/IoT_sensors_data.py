import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field 
from models.geographic_data import GeographicData

class IoTSensorsData(BaseModel):
    sensor_Id: str
    sensor_type: str
    sensor_location: Optional[str]
    sensor_station: Optional[str]
    sensor_depth: Optional[str]
    soil_light_intensity: Optional[float]
    soil_light_illumination_duration_days: Optional[float]
    phosphorus_concentration: Optional[float]
    potassium_concentration: Optional[float]
    CO2_concentration: Optional[float]
    data_source: Optional[str]
    geographic_id: GeographicData = Field(..., alias="geographic_id")