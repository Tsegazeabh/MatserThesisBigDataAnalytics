from typing import Any, Dict
from pydantic import BaseModel, Field

class SoilData(BaseModel):
   data: Dict[str, Any] = {
                           "soil_name":"soil_name",
                           "soil_type":"soil_type",
                           "soil_pH":"soil_pH",
                           "soil_CEC":"soil_CEC",
                           "soil_salinity":"soil_salinity",
                           "soil_bulk_density":"soil_bulk_density",
                           "soil_OC":"soil_OC",
                           "soil_clay":"soil_clay",        
                           "soil_phosphorus":"soil_phosphorus",
                           "soil_potassium":"soil_potassium",
                           "soil_temperature":"soil_temperature",
                           "soil_moisture":"soil_moisture",
                           "soil_electrical_conductivity":"soil_electrical_conductivity",
                           "data_source":"data_source"
                        }
   geographic_id: str = Field(..., alias="geographic_id")
