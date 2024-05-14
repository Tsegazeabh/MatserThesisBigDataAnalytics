from typing import List


def topographyDataEntity(item) -> dict:
    return {
        "id":str(item["id"]),
        "slope":item["slope"],
        "aspect":item["aspect"],
        "altitude":item["altitude"],
        "topography_type":item["topography_type"],
        "ground_area_coverage_km2":item["ground_area_coverage_km2"],
        "data_source":item["data_source"],
        "geographic_id":item["geographic_id"]
    }
def topographysDataEntity(entity) -> List:
    return [topographyDataEntity(item) for item in entity]