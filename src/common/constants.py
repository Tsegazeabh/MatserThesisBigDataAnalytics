SERVER_PORT = 8002
SERVER_HOST = "localhost"
ROOT_URL = "/pbda/v0"
VERSION = "0.1.4"
# This URL is used to fetch forecast weather data for the next 9 days
MET_FORECAST_URL = "https://api.met.no/weatherapi/locationforecast/2.0/complete"
# This user agent is used for the weather forecast data fetching authorization
MET_USER_AGENT = "259646@usn.no"
# This URL is used to fetch weather history data from MET Frost API services
MET_OBSERVATIONS_URL = "https://frost.met.no/observations/v0.jsonld"
# This client ID is used for weather history data fetching authorization
MET_CLIENT_ID = "732d88c6-1b10-1423-8c2b-45743216781"
# This URL is used to fetch soil data from ISRIC soilgrids API services
ISRIC_SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
# The parameters dict is a sample default setting used as a header for weather history data fetching (can be modified)
MET_WEATHER_PARAMETERS = {
    "sources": "SN17850", # For ÅS NMBU station Id
    "elements": "best_estimate_mean(air_temperature P1D), best_estimate_sum(precipitation_amount P1D), mean(relative_humidity P1D), mean(wind_speed P1D), mean(surface_air_pressure P1D)",
    "referencetime": "2024-01-01/2024-03-01",
    "levels":"default",
    "timeoffsets": "default"
}

# This are the default weather data features
DEFAULT_WEATHER_FEATURES = ["mean(air_temperature P1D)", 
                            "mean(relative_humidity P1D)",
                            "sum(precipitation_amount P1D)",                            
                            "mean(soil_temperature P1D)",
                            "mean(wind_speed P1D)",
                            "mean(surface_air_pressure P1D)",
                            "best_estimate_mean(air_temperature P1D)",
                            "best_estimate_sum(precipitation_amount P1D)"
                            ]
DEFAULT_SOIL_FEATURES = {
                        "depth":[
                            "0-5cm",
                            "0-30cm",
                            "5-15cm",
                            "15-30cm",
                            "30-60cm"
                        ],
                        "value":[
                            "Q0.5",
                            "mean",
                            "uncertainty"
                        ],
                        "data_features":{
                            "bdod":"cg/cm³",
                            "cec":"mmol(c)/kg",
                            "clay":"g/kg",
                            "nitrogen":"cg/kg",
                            "ocd":"hg/m³",
                            "phh2o":"pH",
                            "sand":"g/kg",
                            "silt":"g/kg",
                            "soc":"dg/kg"
                        }			
                    }
DEFAULT_OPEN_WEATHER_FEATURES =[
                                "temp",
                                "temp_min",
                                "temp_max",
                                "pressure",
                                "humidity",
                                "speed",
                                "deg"
                                ]

# Configure this path to locate the exported static files destination
STATIC_FILES_OUTPUT_PATH = "src/files/data/outputs"
OPEN_WEATHER_API_KEY = "add-your-open-weather-key"
OPEN_WEATHER_HOSTORY_URL = "https://history.openweathermap.org/data/2.5/history/city"
ZP_REPORT_FETCHING_URL = "https://feature-extraction-value-zu3hsmhdza-nw.a.run.app/api/v0/extractInfo"
BIG_AGRI_DATASET_FORMAT = {
                            "meta_data": {
                                "dataset_name":"Big Agri Data",
                                "created_by": "Tsegazeab Hailu Tedla",
                                "created_on": "time stamp",
                                "user_id": "17959",
                                "description": "Dataset description"
                            },
                            "farmland_location": {
                                "latitude": 59.6605,
                                "longitude": 10.7818,
                                "altitude": 93.3,
                                "farm_identifier":"23444",
                                "farm_size": 234,
                                "nearby_source_station_id":"SN17850"
                            },
                            "referencetime": {
                                "from_date": "2024-01-01",
                                "to_date": "2024-02-01"
                            },
                            "data_source_types": {
                                "weather":{
                                    "method":"upload",
                                    "source":"LOCAL",
                                    "request_type":"file",
                                    "depth":[
                                    ],
                                    "value":[
                                    ],
                                    "data_features":{
                                    }
                                },
                                "soil":{
                                    "method":"upload",
                                    "source":"Local",
                                    "request_type":"http",
                                    "depth":[
                                    ],
                                    "value":[
                                    ],
                                    "data_features":{
                                    }
                                },
                                "IoT_sensors":{
                                    "method":"upload",
                                    "source":"LOCAL",
                                    "request_type":"http",
                                    "depth":[
                                    ],
                                    "value":[
                                    ],
                                    "data_features":{
                                    }
                                },
                                "crop":{
                                    "method":"upload",
                                    "source":"LOCAL",
                                    "request_type":"http",
                                    "depth":[
                                    ],
                                    "value":[
                                    ],
                                    "data_features":{
                                    }
                                },
                                "farming_practice":{
                                    "method":"upload",
                                    "source":"LOCAL",
                                    "request_type":"http",
                                    "depth":[
                                    ],
                                    "value":[
                                    ],
                                    "data_features":{
                                    }
                                },
                                "agrisenze":{
                                    "method":"upload",
                                    "source":"LOCAL",
                                    "request_type":"http",
                                    "depth":[
                                    ],
                                    "value":[
                                    ],
                                    "data_features":{
                                    }
                                },
                                "VI":{
                                    "method":"upload",
                                    "source":"LOCAL",
                                    "request_type":"http",
                                    "depth":[
                                    ],
                                    "value":[
                                    ],
                                    "data_features":{
                                    }
                                },
                                "topography":{
                                    "method":"upload",
                                    "source":"LOCAL",
                                    "request_type":"http",
                                    "depth":[
                                    ],
                                    "value":[
                                    ],
                                    "data_features":{
                                    }
                                }
                            }
                        }

