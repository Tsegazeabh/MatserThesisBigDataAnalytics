from typing import List


def agrisenzeDataEntity(item) -> dict:
    return {
        "id":str(item["id"]),
        "sensor_Id":item["sensor_Id"],
        "sensor_location":item["sensor_location"],
        "sensor_station":item["sensor_station"],
        "sensor_depth":item["sensor_depth"],
        "nitrate_concentration":item["nitrate_concentration"],
        "reading_date":item["reading_date"],
        "data_source":item["data_source"],
        "geographic_id":item["geographic_id"]
    }
def agrisenzesDataEntity(entity) -> List:
    return [agrisenzeDataEntity(item) for item in entity]