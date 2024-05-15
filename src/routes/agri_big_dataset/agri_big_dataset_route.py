from datetime import datetime, date
from typing import Any, Dict, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from common import constants as const
from utils.firebase_storage import db
from models.agri_big_dataset import AgriBigDataset, SoilDataFeatures, WeatherDataFeatures
from services import IoT_sensors_service, soil_service, weather_service, crop_service, agrisenze_service, farming_practice_service, geographic_service, VI_data_service, topographic_service
from pydantic import Json, BaseModel, ValidationError

#========================================================
# Agri Big Data API End Points Router Implementation
#========================================================
agriBigDataset = APIRouter(tags=["Build Agri Big Dataset APIs"])

# Collection reference
agri_big_dataset_ref = db.collection("agri_big_data")
    
@agriBigDataset.post("/generateAgriBigDataset")
async def process_agri_big_dataset(dataset_format: Json = Form( default=const.BIG_AGRI_DATASET_FORMAT, title='Big Agri Dataset Format',description='Enter the pre-formatted JSON configuration and data (Follow recommended JSON format)'),
                                   weather_csv_file: UploadFile = File(None, media_type=["text/csv", "application/vnd.ms-excel"], description='Upload the weather data in csv/excel file format'), 
                                   soil_csv_file: UploadFile = File(None, media_type=["text/csv", "application/vnd.ms-excel"], description='Upload the soil data in csv/excel file format'), 
                                   crop_csv_file: UploadFile = File(None, media_type=["text/csv", "application/vnd.ms-excel"], description='Upload the crop data in csv/excel file format'), 
                                   agrisenze_csv_file: UploadFile = File(None, media_type=["text/csv", "application/vnd.ms-excel"], description='Upload the agrisenze data in csv/excel file format'),
                                   IoT_sensors_csv_file: UploadFile = File(None, media_type=["text/csv", "application/vnd.ms-excel"], description='Upload the IOT sensors data in csv/excel file format'),
                                   farming_practice_csv_file: UploadFile = File(None, media_type=["text/csv", "application/vnd.ms-excel"], description='Upload the farming practices data in csv/excel file format'),
                                   VI_csv_file: UploadFile = File(None, media_type=["text/csv", "application/vnd.ms-excel"], description='Upload the vegetation indices data in csv/excel file format'),
                                   topography_csv_file: UploadFile = File(None, media_type=["text/csv", "application/vnd.ms-excel"], description='Upload the topography data in csv/excel file format')                                   
                                   ):
    try: 
        # Convert date strings to date objects
        today = date.today()
        from_date = datetime.strptime(dataset_format["referencetime"]["from_date"], "%Y-%m-%d").date()
        to_date = datetime.strptime(dataset_format["referencetime"]["to_date"], "%Y-%m-%d").date()
        if from_date < today and to_date < today:
            dataset_requested = AgriBigDataset(**dataset_format)

            # Initialize the dictionary response objects of the different data source types
            weather_data_response = {}
            soil_data_response = {}
            crop_data_response ={}
            IoT_sensors_data_response ={}
            agrisenze_data_response ={}
            topography_data_response ={}
            farming_practice_data_response= {}
            VI_data_response ={}

            for data_source_type, data_source_info in dataset_requested.data_source_types.items():
                if data_source_type == "weather":
                    weather_data_info: Optional[WeatherDataFeatures] = dataset_requested.data_source_types.get("weather")
                    method = weather_data_info.method
                    if method == "select" or method == "default":
                        if(weather_data_info.data_features != {}):
                            # Implement logic to fetch data based on the selected source and period
                            weather_data_response = await weather_service.fetch_weather_data_features(data_source_info, dataset_requested.farmland_location, dataset_requested.referencetime)
                            
                        else:
                            weather_data_response = {}
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files
                        # Use data_files[data_source_type] to access the uploaded file
                        weather_data_response = await weather_service.upload_weather_data_features(weather_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "soil":                
                    soil_data_info: Optional[SoilDataFeatures] = dataset_requested.data_source_types.get("soil")
                    method = soil_data_info.method               
                    if method == "select" or method=="default":
                        # Implement logic to fetch data based on the selected source and period
                        if(soil_data_info.data_features != {}):
                            soil_data_response = await soil_service.fetch_soil_data_features(soil_data_info, dataset_requested.farmland_location)
                        else:
                            soil_data_response = {}
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        soil_data_response = await soil_service.upload_soil_data_features(soil_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "crop":
                    crop_data_info = dataset_requested.data_source_types.get("crop")
                    method = crop_data_info.method
                    if method == "select" or method=="default":
                        if(crop_data_info.data_features != {}):
                            crop_data_response ={}
                            # TODO: Implement logic to fetch data based on the selected source and period
                            # crop_data_response = await crop_service.fetch_crop_data_features(crop_data_info, farmland_location)
                        else:
                            crop_data_response ={}
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        crop_data_response = await crop_service.upload_crop_data_features(crop_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "IoT_sensors":
                    IoT_sensors_data_info = dataset_requested.data_source_types.get("IoT_sensors")
                    method = IoT_sensors_data_info.method
                    if method == "select" or method=="default":
                        if(IoT_sensors_data_info.data_features != {}):
                            IoT_sensors_data_response ={}
                            # TODO: Implement logic to fetch data based on the selected source and period
                            # IoT_sensors_data_response = await IoT_sensors_service.fetch_IoT_sensors_data_features(IoT_sensors_data_info, farmland_location)
                        else:
                            IoT_sensors_data_response ={}
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        IoT_sensors_data_response = await IoT_sensors_service.upload_IoT_sensors_data_features(IoT_sensors_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "farming_practice":
                    farming_practice_data_info = dataset_requested.data_source_types.get("farming_practice")
                    method = farming_practice_data_info.method
                    if method == "select" or method=="default":
                        if(crop_data_info.data_features != {}):
                            crop_data_response ={}
                            # TODO: Implement logic to fetch data based on the selected source and period
                            # farming_practice_data_response = await farming_practice_service.fetch_farming_practice_data_features(farming_practice_data_info, farmland_location)
                        else:
                            crop_data_response ={}
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        farming_practice_data_response = await farming_practice_service.upload_farming_practice_data_features(farming_practice_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "agrisenze":
                    agrisenze_data_info = dataset_requested.data_source_types.get("agrisenze")
                    method = agrisenze_data_info.method
                    if method == "select" or method=="default":
                        if(agrisenze_data_info.data_features != {}):
                            agrisenze_data_response ={}
                            # TODO: Implement logic to fetch data based on the selected source and period
                            # agrisenze_data_response = await agrisenze_service.fetch_agrisenze_data_features(agrisenze_data_info, farmland_location)
                        else:
                            agrisenze_data_response ={}
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        agrisenze_data_response = await agrisenze_service.upload_agrisenze_data_features(agrisenze_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "topography":
                    topography_data_info = dataset_requested.data_source_types.get("topography")
                    method = topography_data_info.method
                    if method == "select" or method=="default":
                        if(topography_data_info.data_features != {}):
                            topography_data_response ={}
                            # TODO: Implement logic to fetch data based on the selected source and period
                            # topography_data_response = await topography_service.fetch_topography_data_features(topography_data_info, farmland_location)
                        else:
                            topography_data_response ={}
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        topography_data_response = await topographic_service.upload_topography_data_features(topography_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")  
                elif data_source_type == "VI":
                    VI_data_info = dataset_requested.data_source_types.get("VI")
                    method = VI_data_info.method
                    if method == "select" or method=="default":
                        if(VI_data_info.data_features != {}):
                            VI_data_response ={}
                            # TODO: Implement logic to fetch data based on the selected source and period
                            # VI_data_response = await VI_service.fetch_VI_data_features(VI_data_info, farmland_location)
                        else:
                            VI_data_response ={}
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        VI_data_response = await VI_data_service.upload_VI_data_features(VI_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")          
                else:
                    raise HTTPException(status_code=500, detail="No data source type selected. Please select at least one data source type!")
            
            agri_big_dataset_dict = {
                'meta_data': dataset_requested.meta_data, 
                'farmland_location_data': dataset_requested.farmland_location, 
                'referencetime': dataset_requested.referencetime, 
                'weather_data': weather_data_response, 
                'soil_data': soil_data_response, 
                'crop_data': crop_data_response, 
                'IoT_sensors_data': IoT_sensors_data_response, 
                'farming_practice_data': farming_practice_data_response, 
                'agrisenze_data': agrisenze_data_response, 
                'VI_data': VI_data_response,
                'topography_data': topography_data_response
            }
            data_dict: Dict[Any, Any] = agri_big_dataset_dict        
            doc_ref = agri_big_dataset_ref.add(data_dict)
            # Retrieve the inserted document using its ID
            inserted_document = agri_big_dataset_ref.document(doc_ref[1].id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                agri_big_dataset_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                agri_big_dataset_dict["id"] = doc_ref[1].id
                return agri_big_dataset_dict
            else:
                raise HTTPException(status_code=500, detail="Inserted document is not found")
        else:
            raise HTTPException(status_code=500, detail="Enter past from/to reference times")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}Something went wrong. Please try again!")