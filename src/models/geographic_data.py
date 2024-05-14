import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel

class GeographicData(BaseModel):
    latitude:float
    longitude:float
    altitude:float
    farm_identifier: str
    nearby_source_station_id:str
    farm_size: float