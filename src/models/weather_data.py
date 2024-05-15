from typing import Any, Dict
from pydantic import BaseModel, Field 

class WeatherData(BaseModel):
    data: Dict[str, Any] = {
                            "best_estimate_mean_air_temperature_P1M":"best_estimate_mean_air_temperature_P1M",
                            "best_estimate_sum_precipitation_amount_P1M":"best_estimate_sum_precipitation_amount_P1M",
                            "mean_relative_humidity_P1M":"mean_relative_humidity_P1M",
                            "mean_wind_speed_P1M":"mean_wind_speed_P1M",
                            "mean_surface_air_pressure_P1M":"mean_surface_air_pressure_P1M",
                            "best_estimate_mean_air_temperature_P1D":"best_estimate_mean_air_temperature_P1D",
                            "best_estimate_sum_precipitation_amount_P1D":"best_estimate_sum_precipitation_amount_P1D",
                            "mean_relative_humidity_P1D":"mean_relative_humidity_P1D",
                            "mean_wind_speed_P1D":"mean_wind_speed_P1D",
                            "mean_surface_air_pressure_P1D":"mean_surface_air_pressure_P1D",
                            "data_source":"data_source"
                         }
    geographic_id: str = Field(..., alias="geographic_id")