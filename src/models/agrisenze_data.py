import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from models.geographic_data import GeographicData

class AgriSenzeData(BaseModel):
    sensor_Id:str
    sensor_location:str
    sensor_station:str
    sensor_depth:float    
    nitrate_concentration:float
    reading_date:str
    data_source: Optional[str]
    geographic_id: str = Field(..., alias="geographic_id")
    
