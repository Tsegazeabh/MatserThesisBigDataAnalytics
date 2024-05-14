from datetime import datetime, date
from typing import Any, Dict, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from common import constants as const
from utils.firebase_storage import db
from models.agri_big_dataset import AgriBigDataset, SoilDataFeatures
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
        print('Entered to endpoint')
        # Convert date strings to date objects
        today = date.today()
        from_date = datetime.strptime(dataset_format["referencetime"]["from_date"], "%Y-%m-%d").date()
        to_date = datetime.strptime(dataset_format["referencetime"]["to_date"], "%Y-%m-%d").date()
        if from_date < today and to_date < today:
            dataset_requested = AgriBigDataset(**dataset_format)
            print("Dataset Requested: ", dataset_requested)
            print("Source Type:", dataset_requested.data_source_types)

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
                print("Data Source Info: ", data_source_info)
                print("Data Source Type: ", data_source_type)
                if data_source_type == "weather":
                    # weather_data_info: Optional[WeatherDataFeatures] = dataset_requested.data_source_types.get("weather")
                    method = data_source_info.method
                    if (method == "select" and data_source_info.data_features is not None) or method =="default":
                        # Implement logic to fetch data based on the selected source and period
                        weather_data_response = await weather_service.fetch_weather_data_features(data_source_info, dataset_requested.farmland_location, dataset_requested.referencetime)
                        print("weather fetched successfully")
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files
                        # Use data_files[data_source_type] to access the uploaded file
                        weather_data_response = await weather_service.upload_weather_data_features(weather_csv_file)
                        print('Weather Data Response Upload:', weather_data_response)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "soil":                
                    soil_data_info: Optional[SoilDataFeatures] = dataset_requested.data_source_types.get("soil")
                    method = soil_data_info.method
                    print("method:", soil_data_info.method)
                    print("source:", soil_data_info.source)
                    print("request_type:", soil_data_info.request_type)
                    print("depth:", soil_data_info.depth)
                    print("value:", soil_data_info.value)
                    print("data_features:", soil_data_info.data_features)                
                    if method == "select" or method=="default":
                        # Implement logic to fetch data based on the selected source and period
                        soil_data_response = await soil_service.fetch_soil_data_features(soil_data_info, dataset_requested.farmland_location)
                        print('soil data returned successfully')
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        soil_data_response = await soil_service.upload_soil_data_features(soil_csv_file)
                        print('soil data uploaded successfully')
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "crop":
                    crop_data_info = dataset_requested.data_source_types.get("crop")
                    method = crop_data_info.method
                    if method == "select" or method=="default":
                        # TODO Implement logic to fetch data based on the selected source and period
                        # crop_data_response = await crop_service.fetch_crop_data_features(soil_data_info, farmland_location)
                        print('crop data returned successfully')
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        crop_data_response = await crop_service.upload_crop_data_features(crop_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "IoT_sensors":
                    IoT_sensors_data_info = dataset_requested.data_source_types.get("IoT_sensors")
                    method = IoT_sensors_data_info.method
                    if method == "select" or method=="default":
                        # TODO Implement logic to fetch data based on the selected source and period
                        # IoT_sensors_data_response = await IoT_sensors_service.fetch_IoT_sensors_data_features(IoT_sensors_data_info, farmland_location)
                        print('IoT sensors data returned successfully')
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        IoT_sensors_data_response = await IoT_sensors_service.upload_IoT_sensors_data_features(IoT_sensors_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "farming_practice":
                    farming_practice_data_info = dataset_requested.data_source_types.get("farming_practice")
                    method = farming_practice_data_info.method
                    if method == "select" or method=="default":
                        # TODO Implement logic to fetch data based on the selected source and period
                        # farming_practice_data_response = await farming_practice_service.fetch_farming_practice_data_features(farming_practice_data_info, farmland_location)
                        print('Farming practice data returned successfully')
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        farming_practice_data_response = await farming_practice_service.upload_farming_practice_data_features(farming_practice_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "agrisenze":
                    agrisenze_data_info = dataset_requested.data_source_types.get("agrisenze")
                    method = agrisenze_data_info.method
                    if method == "select" or method=="default":
                        # TODO Implement logic to fetch data based on the selected source and period
                        # agrisenze_data_response = await agrisenze_service.fetch_agrisenze_data_features(agrisenze_data_info, farmland_location)
                        print('Agrisenze data returned successfully')
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        agrisenze_data_response = await agrisenze_service.upload_agrisenze_data_features(agrisenze_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")
                elif data_source_type == "topography":
                    topography_data_info = dataset_requested.data_source_types.get("topography")
                    method = topography_data_info.method
                    if method == "select" or method=="default":
                        # TODO Implement logic to fetch data based on the selected source and period 
                        # topography_data_response = await topography_service.fetch_topography_data_features(topography_data_info, farmland_location)
                        print('Topography data returned successfully')
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        topography_data_response = await topographic_service.upload_topography_data_features(topography_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")  
                elif data_source_type == "VI":
                    topography_data_info = dataset_requested.data_source_types.get("VI")
                    method = topography_data_info.method
                    if method == "select" or method=="default":
                        # TODO Implement logic to fetch data based on the selected source and period
                        # VI_data_response = await VI_service.fetch_VI_data_features(VI_data_info, farmland_location)
                        print('VI data returned successfully')
                    elif method == "upload":
                        # Implement logic to upload data from uploaded files                    
                        VI_data_response = await VI_data_service.upload_VI_data_features(VI_csv_file)
                    else:
                        raise HTTPException(status_code=500, detail="Invalid method selected")          
                else:
                    pass
            
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
            print("Added to database successfully")
            inserted_document = agri_big_dataset_ref.document(doc_ref[1].id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                agri_big_dataset_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                agri_big_dataset_dict["id"] = doc_ref[1].id
                return agri_big_dataset_dict
            else:
                raise HTTPException(status_code=500, detail="Inserted document not found")
        else:
            raise HTTPException(status_code=500, detail="Enter past from/to reference times")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# async def process_agri_big_dataset(dataset_requested: AgriBigDataset):
#     try:
#         print('Entered to endpoint')
#         for data_source_type, data_source_info in dataset_requested.data_source_types.items():            
#             print(data_source_info)
#             if data_source_type == "weather":
#                 weather_data_info: Optional[WeatherDataFeatures] = dataset_requested.data_source_types.get("weather")
#                 method = weather_data_info.method
#                 if method == "select" or method =="default":
#                     # Implement logic to fetch data based on the selected source and period
#                     weather_data_response = await weather_service.fetch_weather_data_features(data_source_info, dataset_requested.farmland_location, dataset_requested.referencetime)
#                     print("weather fetched successfully")
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                     weather_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             elif data_source_type == "soil":                
#                 soil_data_info: Optional[SoilDataFeatures] = dataset_requested.data_source_types.get("soil")
#                 method = soil_data_info.method
#                 print("method:", soil_data_info.method)
#                 print("source:", soil_data_info.source)
#                 print("request_type:", soil_data_info.request_type)
#                 print("depth:", soil_data_info.depth)
#                 print("value:", soil_data_info.value)
#                 print("data_features:", soil_data_info.data_features)                
#                 if method == "select":
#                     # Implement logic to fetch data based on the selected source and period
#                     soil_data_response = await soil_service.fetch_soil_data_features(soil_data_info, dataset_requested.farmland_location)
#                     print('Wather data returned successfully')
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                     soil_data_response = {}
#                 elif method == "default":
#                     # Implement logic to use default data
#                     # Ignore the incoming 'data' object and use predefined data
#                     soil_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             elif data_source_type == "crop":
#                 crop_data_info = dataset_requested.data_source_types.get("crop")
#                 method = crop_data_info.method
#                 if method == "select":
#                     # Implement logic to fetch data based on the selected source and period
#                     # Use data_source_info["source"] and data_source_info["period"] to fetch data
#                     crop_data_response = {}
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                    crop_data_response = {}
#                 elif method == "default":
#                     # Implement logic to use default data
#                     # Ignore the incoming 'data' object and use predefined data
#                     crop_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             elif data_source_type == "IoT_sensors":
#                 IoT_sensors_data_info = dataset_requested.data_source_types.get("crop")
#                 method = IoT_sensors_data_info.method
#                 if method == "select":
#                     # Implement logic to fetch data based on the selected source and period
#                     # Use data_source_info["source"] and data_source_info["period"] to fetch data
#                     IoT_sensors_data_response = {}
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                     IoT_sensors_data_response = {}
#                 elif method == "default":
#                     # Implement logic to use default data
#                     # Ignore the incoming 'data' object and use predefined data
#                     IoT_sensors_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             elif data_source_type == "farming_practice":
#                 farming_practice_data_info = dataset_requested.data_source_types.get("crop")
#                 method = farming_practice_data_info.method
#                 if method == "select":
#                     # Implement logic to fetch data based on the selected source and period
#                     # Use data_source_info["source"] and data_source_info["period"] to fetch data
#                     farming_practice_data_response = {}
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                     farming_practice_data_response = {}
#                 elif method == "default":
#                     # Implement logic to use default data
#                     # Ignore the incoming 'data' object and use predefined data
#                     farming_practice_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             elif data_source_type == "agrisenze":
#                 agrisenze_data_info = dataset_requested.data_source_types.get("crop")
#                 method = agrisenze_data_info.method
#                 if method == "select":
#                     # Implement logic to fetch data based on the selected source and period
#                     # Use data_source_info["source"] and data_source_info["period"] to fetch data
#                     agrisenze_data_response = {}
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                     agrisenze_data_response = {}
#                 elif method == "default":
#                     # Implement logic to use default data
#                     # Ignore the incoming 'data' object and use predefined data
#                     agrisenze_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             elif data_source_type == "topography":
#                 topography_data_info = dataset_requested.data_source_types.get("crop")
#                 method = topography_data_info.method
#                 if method == "select":
#                     # Implement logic to fetch data based on the selected source and period
#                     # Use data_source_info["source"] and data_source_info["period"] to fetch data
#                     topography_data_response = {}
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                     topography_data_response = {}
#                 elif method == "default":
#                     # Implement logic to use default data
#                     # Ignore the incoming 'data' object and use predefined data
#                     topography_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             elif data_source_type == "fertilizer":
#                 fertilizer_data_info = dataset_requested.data_source_types.get("crop")
#                 method = fertilizer_data_info.method
#                 if method == "select":
#                     # Implement logic to fetch data based on the selected source and period
#                     # Use data_source_info["source"] and data_source_info["period"] to fetch data
#                     fertilizer_data_response = {}
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                     fertilizer_data_response = {}
#                 elif method == "default":
#                     # Implement logic to use default data
#                     # Ignore the incoming 'data' object and use predefined data
#                     fertilizer_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             elif data_source_type == "pesticide":
#                 pesticide_data_info = dataset_requested.data_source_types.get("crop")
#                 method = pesticide_data_info.method
#                 if method == "select":
#                     # Implement logic to fetch data based on the selected source and period
#                     # Use data_source_info["source"] and data_source_info["period"] to fetch data
#                     pesticide_data_response = {}
#                 elif method == "upload":
#                     # Implement logic to upload data from uploaded files
#                     # Use data_files[data_source_type] to access the uploaded file
#                     pesticide_data_response = {}
#                 elif method == "default":
#                     # Implement logic to use default data
#                     # Ignore the incoming 'data' object and use predefined data
#                     pesticide_data_response = {}
#                 else:
#                     raise HTTPException(status_code=400, detail="Invalid method selected")
#             else:
#                 pass
#         # If any of the data source types are not requested, return empty objects
#         if 'weather' not in dataset_requested.data_source_types:
#             weather_data_response ={}
#         if 'soil' not in dataset_requested.data_source_types:
#             soil_data_response = {}
#         if 'crop' not in dataset_requested.data_source_types:
#             crop_data_response = {}
#         if 'IoT_sensors' not in dataset_requested.data_source_types:
#             IoT_sensors_data_response = {}
#         if 'farming_practice' not in dataset_requested.data_source_types:
#             farming_practice_data_response = {}
#         if 'agrisenze' not in dataset_requested.data_source_types:
#             agrisenze_data_response = {}
#         if 'topography' not in dataset_requested.data_source_types:
#             topography_data_response = {}
#         if 'fertilizer' not in dataset_requested.data_source_types:
#             fertilizer_data_response = {}
#         if 'pesticide' not in dataset_requested.data_source_types:
#             pesticide_data_response = {}
#         # Save to database if saving is active
#         # Convert agrisenzeData object to dictionary
#         agri_big_dataset_dict = {
#             'meta_data':dataset_requested.meta_data, 
#             'farmland_location':dataset_requested.farmland_location, 
#             'referencetime': dataset_requested.referencetime, 
#             'weather_data_response':weather_data_response, 
#             'soil_data_response': soil_data_response, 
#             'crop_data_response':crop_data_response, 
#             'IoT_sensors_data_response':IoT_sensors_data_response, 
#             'farming_practice_data_response':farming_practice_data_response, 
#             'agrisenze_data_response':agrisenze_data_response, 
#             'topography_data_response':topography_data_response, 
#             'fertilizer_data_response':fertilizer_data_response, 
#             'pesticide_data_response':pesticide_data_response
#         }
#         data_dict: Dict[str, Any] = agri_big_dataset_dict
#         # Add the AgriSenze to the agrisenze_data collection
#         doc_ref = agri_big_dataset_ref.add(data_dict)
#         # Retrieve the inserted document using its ID
#         inserted_document = agri_big_dataset_ref.document(doc_ref[1].id).get()
#         if inserted_document.exists:
#             # Convert the inserted document to a dictionary
#             agri_big_dataset_dict = inserted_document.to_dict()
#             # Add the document ID to the dictionary
#             agri_big_dataset_dict["id"] = doc_ref[1].id
#             return agri_big_dataset_dict
#         else:
#             raise HTTPException(status_code=404, detail="Inserted document not found")
#         # return {
#         #     'meta_data':dataset_requested.meta_data, 
#         #     'farmland_location':dataset_requested.farmland_location, 
#         #     'referencetime': dataset_requested.referencetime, 
#         #     'weather_data_response':weather_data_response, 
#         #     'soil_data_response': soil_data_response, 
#         #     'crop_data_response':crop_data_response, 
#         #     'IoT_sensors_data_response':IoT_sensors_data_response, 
#         #     'farming_practice_data_response':farming_practice_data_response, 
#         #     'agrisenze_data_response':agrisenze_data_response, 
#         #     'topography_data_response':topography_data_response, 
#         #     'fertilizer_data_response':fertilizer_data_response, 
#         #     'pesticide_data_response':pesticide_data_response
#         # }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))