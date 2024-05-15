from typing import Any, Dict
from pydantic import BaseModel, Field

class CropData(BaseModel):
    data: Dict[str, Any] ={
                            "crop_type":"crop_type",
                            "crop_planting_date":"crop_planting_date",
                            "crop_harvesting_date":"crop_harvesting_date",
                            "crop_yield":"crop_yield",
                            "crop_residue":"crop_residue",
                            "crop_biomass":"crop_biomass",
                            "crop_rotation_type":"crop_rotation_type",
                            "average_number_of_crops_rotated_per_3years":"average_number_of_crops_rotated_per_3years",
                            "data_source":"data_source"
                        }
    geographic_id: str = Field(..., alias="geographic_id")