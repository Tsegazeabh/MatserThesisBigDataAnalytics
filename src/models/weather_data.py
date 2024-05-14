from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field 
from models.geographic_data import GeographicData

class WeatherData(BaseModel):
    best_estimate_mean_air_temperature_P1M : Optional[float]
    best_estimate_sum_precipitation_amount_P1M :Optional[float]
    mean_relative_humidity_P1M :Optional[float]
    mean_wind_speed_P1M: Optional[float]
    mean_surface_air_pressure_P1M: Optional[float]
    best_estimate_mean_air_temperature_P1D :Optional[float]
    best_estimate_sum_precipitation_amount_P1D :Optional[float]
    mean_relative_humidity_P1D :Optional[float]
    mean_wind_speed_P1D: Optional[float]
    mean_surface_air_pressure_P1D: Optional[float]
    data_source: Optional[str]
    geographic_id: GeographicData = Field(..., alias="geographic_id")