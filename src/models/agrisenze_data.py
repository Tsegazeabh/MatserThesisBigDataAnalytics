import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from models.geographic_data import GeographicData

class AgriSenzeData(BaseModel):
    data: Dict[str, Any] = {"sensor_Id":"ID4",
                            "sensor_location":"AS",
                            "sensor_station":"NMBU",
                            "sensor_depth":"40",
                            "nitrate_concentration":"60",
                            "data_source":"ZP",
                            "day":"01",
                            "month":"07",
                            "year":"2024"}
    geographic_id: str = Field(..., alias="geographic_id")
    
