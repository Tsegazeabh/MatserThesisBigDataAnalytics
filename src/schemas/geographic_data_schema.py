from typing import List


def geographicDataEntity(item) -> dict:
    return {
        "id":str(item["id"]),
        "latitude":item["latitude"],
        "longitude":item["longitude"],
        "altitude":item["altitude"],
        "farm_identifier":item["farm_identifier"],
        "nearby_source_station_id":item["nearby_source_station_id"],
        "farm_size":item["farm_size"]
    }
def geographicsDataEntity(entity) -> List:
    return [geographicDataEntity(item) for item in entity]