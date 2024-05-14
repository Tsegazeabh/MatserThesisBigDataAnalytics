from typing import List


def soilDataEntity(item) -> dict:
    return {
        "id":str(item["id"]),
        "soil_name":item["soil_name"],
        "soil_type":item["soil_type"],
        "soil_pH":item["soil_pH"],
        "soil_CEC":item["soil_CEC"],
        "soil_salinity":item["soil_salinity"],
        "soil_bulk_density":item["soil_bulk_density"],
        "soil_OC":item["soil_OC"],
        "soil_clay":item["soil_clay"],        
        "soil_phosphorus":item["soil_phosphorus"],
        "soil_potassium":item["soil_potassium"],
        "soil_temperature":item["soil_temperature"],
        "soil_moisture":item["soil_moisture"],
        "soil_electrical_conductivity":item["soil_electrical_conductivity"],
        "data_source":item["data_source"],
        "geographic_id":item["geographic_id"]     

    }
def soilsDataEntity(entity) -> List:
    return [soilDataEntity(item) for item in entity]