from typing import List


def weatherDataEntity(item) -> dict:
    return {
        "id":str(item["id"]),
        "best_estimate_mean_air_temperature_P1M":item["best_estimate_mean_air_temperature_P1M"],
        "best_estimate_sum_precipitation_amount_P1M":item["best_estimate_sum_precipitation_amount_P1M"],
        "mean_relative_humidity_P1M":item["mean_relative_humidity_P1M"],
        "mean_wind_speed_P1M":item["mean_wind_speed_P1M"],
        "mean_surface_air_pressure_P1M":item["mean_surface_air_pressure_P1M"],
        "best_estimate_mean_air_temperature_P1D":item["best_estimate_mean_air_temperature_P1D"],
        "best_estimate_sum_precipitation_amount_P1D":item["best_estimate_sum_precipitation_amount_P1D"],
        "mean_relative_humidity_P1D":item["mean_relative_humidity_P1D"],
        "mean_wind_speed_P1D":item["mean_wind_speed_P1D"],
        "mean_surface_air_pressure_P1D":item["mean_surface_air_pressure_P1D"],
        "data_source":item["data_source"],
        "geographic_id":item["geographic_id"]
    }
def weathersDataEntity(entity) -> List:
    return [weatherDataEntity(item) for item in entity]