from typing import List


def cropDataEntity(item) -> dict:
    return {
        "id":str(item["id"]),
        "crop_type":item["crop_type"],
        "crop_planting_date":item["crop_planting_date"],
        "crop_harvesting_date":item["crop_harvesting_date"],
        "crop_yield":item["crop_yield"],
        "crop_residue":item["crop_residue"],
        "crop_biomass":item["crop_biomass"],
        "crop_rotation_type":item["crop_rotation_type"],
        "average_number_of_crops_rotated_per_3years":item["average_number_of_crops_rotated_per_3years"],
        "data_source":item["data_source"],
        "geographic_id":item["geographic_id"]
    }
def cropsDataEntity(entity) -> List:
    return [cropDataEntity(item) for item in entity]