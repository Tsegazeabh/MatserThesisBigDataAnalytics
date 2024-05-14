import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4
from click import DateTime
from fastapi import UploadFile
from pydantic import BaseModel, Field

class WeatherDataFeatures(BaseModel):
    method: str
    source: str
    request_type: str
    depth: Optional[List[str]] = None
    value: Optional[List[str]] = None
    data_features: Optional[Dict[str, str]]

class SoilDataFeatures(BaseModel):
    method: str
    source: str
    request_type: str
    depth: Optional[List[str]]
    value: Optional[List[str]]
    data_features: Optional[Dict[str, str]]

class CropDataFeatures(BaseModel):
    method: str
    source: str
    request_type: str
    depth: Optional[List[str]] = None
    value: Optional[List[str]] = None
    data_features: Optional[Dict[str, str]]

class IoTSensorsDataFeatures(BaseModel):
    method: str
    source: str
    request_type: str
    depth: Optional[List[str]] = None
    value: Optional[List[str]] = None
    data_features: Optional[Dict[str, str]]

class FarmingPracticeDataFeatures(BaseModel):
    method: str
    source: str
    request_type: str
    depth: Optional[List[str]] = None
    value: Optional[List[str]] = None
    data_features:Optional[Dict[str, str]]

class AgrisenzeDataFeatures(BaseModel):
    method: str
    source: str
    request_type: str
    depth: Optional[List[str]] = None
    value: Optional[List[str]] = None
    data_features: Optional[Dict[str, str]]

class TopographyDataFeatures(BaseModel):
    method: str
    source: str
    request_type: str
    depth: Optional[List[str]] = None
    value: Optional[List[str]] = None
    data_features: Optional[Dict[str, Union[int, float, str]]]

class VIDataFeatures(BaseModel):
    method: str
    source: str
    request_type: str
    depth: Optional[List[str]] = None
    value: Optional[List[str]] = None
    data_features: Optional[Dict[str, str]]

class AgriBigDataset(BaseModel):
    meta_data: Dict[str, str]
    farmland_location: Dict[str, Union[float, int, str]]
    referencetime: Dict[str, str]
    data_source_types: Dict[str, Optional[Union[SoilDataFeatures, WeatherDataFeatures, CropDataFeatures, IoTSensorsDataFeatures,
                                      FarmingPracticeDataFeatures, AgrisenzeDataFeatures, TopographyDataFeatures,
                                      VIDataFeatures]]]= {}

# class MetaData(BaseModel):
#     dataset_name: str
#     created_by: str
#     created_on: str
#     user_id: str
#     description: str

# class FarmlandLocation(BaseModel):
#     latitude: float
#     longitude: float
#     altitude: float
#     farm_identifier: str
#     farm_size: int
#     nearby_source_station_id: str

# class ReferenceTime(BaseModel):
#     from_date: str
#     to_date: str

# class DataSourceType(BaseModel):
#     method: str
#     source: str
#     request_type: str
#     depth: List[str] = []
#     value: List[str] = []
#     data_features: Dict[str, Union[int, float, str]] = {}

# class DatasetFormRequested(BaseModel):
#     meta_data: MetaData
#     farmland_location: FarmlandLocation
#     referencetime: ReferenceTime
#     data_source_types: Dict[str, DataSourceType]