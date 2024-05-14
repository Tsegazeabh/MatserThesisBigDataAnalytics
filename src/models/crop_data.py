import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from models.geographic_data import GeographicData

class CropData(BaseModel):
    crop_type:str
    crop_name:str
    crop_planting_date:str
    crop_harvesting_date:str
    crop_yield: Optional[float]
    crop_residue:Optional[float]
    crop_biomass:Optional[float]
    crop_rotation_type: Optional[str]
    average_number_of_crops_rotated_per_3years: Optional[int]
    data_source: Optional[str]
    geographic_id: GeographicData = Field(..., alias="geographic_id")