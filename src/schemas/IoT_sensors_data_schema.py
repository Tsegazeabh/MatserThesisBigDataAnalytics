from typing import List


def IoTSensorDataEntity(item) -> dict:
    return {
        "id":str(item["id"]),
        "sensor_Id":item["sensor_Id"],
        "sensor_type":item["sensor_type"],
        "sensor_location":item["sensor_location"],
        "sensor_station":item["sensor_station"],
        "sensor_depth":item["sensor_depth"],
        "phosphorus_concentration":item["phosphorus_concentration"],
        "potassium_concentration":item["potassium_concentration"],
        "soil_light_intensity":item["soil_light_intensity"],
        "soil_light_illumination_duration_days":item["soil_light_illumination_duration_days"],
        "CO2_concentration":item["CO2_concentration"],
        "data_source":item["data_source"],
        "geographic_id":item["geographic_id"]
    }
def IoTSensorsDataEntity(entity) -> List:
    return [IoTSensorDataEntity(item) for item in entity]