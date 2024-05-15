from typing import Any, Dict
from pydantic import BaseModel, Field 

class IoTSensorsData(BaseModel):
    data: Dict[str, Any] = {
                            "sensor_Id":"sensor_Id",
                            "sensor_type":"sensor_type",
                            "sensor_location":"sensor_location",
                            "sensor_station":"sensor_station",
                            "sensor_depth":"sensor_depth",
                            "phosphorus_concentration":"phosphorus_concentration",
                            "potassium_concentration":"potassium_concentration",
                            "soil_light_intensity":"soil_light_intensity",
                            "soil_light_illumination_duration_days":"soil_light_illumination_duration_days",
                            "CO2_concentration":"CO2_concentration",
                            "data_source":"data_source"
                        }
    geographic_id: str = Field(..., alias="geographic_id")