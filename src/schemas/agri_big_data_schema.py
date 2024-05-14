from typing import List

from models.agri_big_dataset import AgriBigDataset, AgrisenzeDataFeatures, CropDataFeatures, FarmingPracticeDataFeatures, IoTSensorsDataFeatures, SoilDataFeatures, TopographyDataFeatures, WeatherDataFeatures

# Then, you can modify your function to return an instance of AgriBigDataset
def bigAgriDataEntity(item) -> AgriBigDataset:
    return AgriBigDataset(
        meta_data={"id": str(item["id"]), "agrisenze_data_id": item["agrisenze_data_id"]},
        farmland_location={"location_id": item["location_id"]},
        referencetime={"some_key": "some_value"},
        data_source_types={
            "soil_data_id": SoilDataFeatures(...),
            "weather_data_id": WeatherDataFeatures(...),
            "crop_data_id": CropDataFeatures(...),
            "IoT_sensors_data_id": IoTSensorsDataFeatures(...),
            "farming_practice_data_id": FarmingPracticeDataFeatures(...),
            "agrisenze_data_id": AgrisenzeDataFeatures(...),
            "topography_data_id": TopographyDataFeatures(...)
        }
    )
def bigAgrisDataEntity(entity) -> List:
    return [bigAgriDataEntity(item) for item in entity]