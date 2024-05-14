from typing import List


def farmingPracticeDataEntity(item) -> dict:
    return {
        "id":str(item["id"]),
        "year":item["year"],
        "season":item["season"],
        "is_cultivation_season":item["is_cultivation_season"],
        "fertilizer_placement_type":item["fertilizer_placement_type"],
        "fertilizer_type":item["fertilizer_type"],
        "seasonal_no_of_fertilizer_applications":item["seasonal_no_of_fertilizer_applications"],
        "is_preplant_stage_fertilizer_applied":item["is_preplant_stage_fertilizer_applied"],
        "is_growth_stage_fertilizer_applied":item["is_growth_stage_fertilizer_applied"],
        "tillage_type":item["tillage_type"],
        "tillage_depth":item["tillage_depth"],
        "tillage_date":item["tillage_date"],
        "population_density":item["population_density"],
        "application_date":item["application_date"],
        "seasonal_irrigation_water_amount":item["seasonal_irrigation_water_amount"],
        "irrigation_date":item["irrigation_date"],
        "data_source":item["data_source"],
        "geographic_id":item["geographic_id"]
    }
def farmingPracticesDataEntity(entity) -> List:
    return [farmingPracticeDataEntity(item) for item in entity]