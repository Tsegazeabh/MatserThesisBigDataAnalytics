from typing import Any, Dict
from pydantic import BaseModel, Field 

class FarmingPracticeData(BaseModel):
    data: Dict[str, Any] = {
                            "year":"year",
                            "season":"season",
                            "is_cultivation_season":"is_cultivation_season",
                            "fertilizer_placement_type":"fertilizer_placement_type",
                            "fertilizer_type":"fertilizer_type",
                            "seasonal_no_of_fertilizer_applications":"seasonal_no_of_fertilizer_applications",
                            "is_preplant_stage_fertilizer_applied":"is_preplant_stage_fertilizer_applied",
                            "is_growth_stage_fertilizer_applied":"is_growth_stage_fertilizer_applied",
                            "tillage_type":"tillage_type",
                            "tillage_depth":"tillage_depth",
                            "tillage_date":"tillage_date",
                            "population_density":"population_density",
                            "application_date":"application_date",
                            "seasonal_irrigation_water_amount":"seasonal_irrigation_water_amount",
                            "irrigation_date":"irrigation_date",
                            "data_source":"data_source"
                        }
    geographic_id: str = Field(..., alias="geographic_id")

    