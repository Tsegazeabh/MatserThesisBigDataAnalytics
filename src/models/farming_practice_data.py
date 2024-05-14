import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from xmlrpc.client import Boolean
from pydantic import BaseModel, Field 
from models.geographic_data import GeographicData

class FarmingPracticeData(BaseModel):
    year: str
    season: str
    is_cultivation_season: str
    fertilizer_placement_type:Optional[str]
    fertilizer_type: Optional[str]
    seasonal_no_of_fertilizer_applications: Optional[int]
    is_preplant_stage_fertilizer_applied: Optional[bool]
    is_growth_stage_fertilizer_applied: Optional[bool]
    tillage_type: Optional[str]
    tillage_depth: Optional[float]
    tillage_date: Optional[str]
    population_density: Optional[float]    
    application_date: Optional[str]
    seasonal_irrigation_water_amount : Optional[float]
    irrigation_date: Optional[float]
    data_source: Optional[str]
    geographic_id: GeographicData = Field(..., alias="geographic_id")

    