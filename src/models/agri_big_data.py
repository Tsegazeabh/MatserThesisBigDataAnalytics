import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from models.agrisenze_data import AgriSenzeData
from models.geographic_data import GeographicData
from models.crop_data import CropData
from models.farming_practice_data import FarmingPracticeData
from models.IoT_sensors_data import IoTSensorsData
from models.soil_data import SoilData
from models.topography_data import TopographyData
from models.weather_data import WeatherData

class AgriBigData(BaseModel):
    location_id: GeographicData = Field(..., alias="location_id")
    agrisenze_data_id: AgriSenzeData = Field(..., alias="agrisenze_data_id")
    crop_data_id: CropData = Field(..., alias="crop_data_id")
    farming_practice_data_id: FarmingPracticeData = Field(..., alias="farming_practice_data_id")
    IoT_sensors_data_id: IoTSensorsData = Field(..., alias="IoT_sensors_data_id")
    soil_data_id: SoilData = Field(..., alias="soil_data_id")
    topography_data_id: TopographyData = Field(..., alias="topography_data_id")
    weather_data_id: WeatherData = Field(..., alias="weather_data_id")
