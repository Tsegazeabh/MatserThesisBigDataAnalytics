import csv
from typing import Any, Dict, Optional
import bson
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import firebase_admin, db
from models.agri_big_data import AgriBigData
from bson import ObjectId
from schemas.agri_big_data_schema import bigAgriDataEntity
import httpx

#========================================================
# Big Agri Data API End Points Router Implementation
#========================================================
agriBigData = APIRouter(tags=["Big Agri Data APIs"])

# Collection reference
agri_big_data_ref = db.collection("agri_big_data")
geographic_data_ref = db.collection("geographic_data")
agrisenze_data_ref = db.collection("agrisenze_data")
crop_data_ref = db.collection("crop_data")
farming_practice_data_ref = db.collection("farming_practice_data")
IoT_sensors_data_ref = db.collection("IoT_sensors_data")
soil_data_ref = db.collection("soil_data")
topography_data_ref = db.collection("topography_data")
weather_data_ref = db.collection("weather_data")

# Define a function to get documents from a collection based on geographic_id
async def get_documents_by_geographic_id(collection_ref, geographic_id):
    documents = []
    query = collection_ref.where("geographic_id", "==", geographic_id).stream()
    for doc in query:
        doc_data = doc.to_dict()
        doc_data["id"] = doc.id
        documents.append(doc_data)
    return documents

# Fetch all big agri data sources using geographic location
@agriBigData.get('/all-agri-data-sources/{geographic_id}')
async def fetch_all_agri_data_sources_by_location(geographic_id):
    try:
        # Get documents from each collection based on the geographic_id
        geographic_data = await get_documents_by_geographic_id(geographic_data_ref, geographic_id)
        agrisenze_data = await get_documents_by_geographic_id(agrisenze_data_ref, geographic_id)
        crop_data = await get_documents_by_geographic_id(crop_data_ref, geographic_id)
        farming_practice_data = await get_documents_by_geographic_id(farming_practice_data_ref, geographic_id)
        IoT_sensors_data = await get_documents_by_geographic_id(IoT_sensors_data_ref, geographic_id)
        soil_data = await get_documents_by_geographic_id(soil_data_ref, geographic_id)
        topography_data = await get_documents_by_geographic_id(topography_data_ref, geographic_id)
        weather_data = await get_documents_by_geographic_id(weather_data_ref, geographic_id)
        
        # Combine data from all collections into a single list
        all_agri_data_sources = {
            "geographic_data": geographic_data,
            "agrisenze_data": agrisenze_data,
            "crop_data": crop_data,
            "farming_practice_data": farming_practice_data,
            "IoT_sensors_data": IoT_sensors_data,
            "soil_data": soil_data,
            "topography_data": topography_data,
            "weather_data": weather_data
        }        
        return {"all_agri_data_sources": all_agri_data_sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define a function to get all documents from a collection
async def get_all_documents(collection_ref):
    documents = []
    query = collection_ref.stream()
    for doc in query:
        doc_data = doc.to_dict()
        doc_data["id"] = doc.id
        documents.append(doc_data)
    return documents

# Fetch all existing big agri data sources
@agriBigData.get('/all-agri-data-sources')
async def fetch_all_agri_data_sources():
    try:
        # Get all documents from each collection
        geographic_data = await get_all_documents(geographic_data_ref)
        agrisenze_data = await get_all_documents(agrisenze_data_ref)
        crop_data = await get_all_documents(crop_data_ref)
        farming_practice_data = await get_all_documents(farming_practice_data_ref)
        IoT_sensors_data = await get_all_documents(IoT_sensors_data_ref)
        soil_data = await get_all_documents(soil_data_ref)
        topography_data = await get_all_documents(topography_data_ref)
        weather_data = await get_all_documents(weather_data_ref)
        
        # Combine data from all collections into a single list
        all_agri_data_sources = {
            "geographic_data": geographic_data,
            "agrisenze_data": agrisenze_data,
            "crop_data": crop_data,
            "farming_practice_data": farming_practice_data,
            "IoT_sensors_data": IoT_sensors_data,
            "soil_data": soil_data,
            "topography_data": topography_data,
            "weather_data": weather_data
        }
        
        return {"all_agri_data_sources": all_agri_data_sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch a big agri data aggregated from different data sources
@agriBigData.post('/fetch-agri-big-data')
async def upload_agri_big_data(geographic_id: str, csv_file: Optional[UploadFile] = File(None), big_agri_form_data: Optional[Dict[str, Any]] = Form(None)):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")

        data_dict = {}
        # Check if data is coming from user input as JSON object or from any API services
        # if agri_big_data is not None:
        #     data_dict = agri_big_data.dict()
        # Check if data is coming from a CSV file
        if csv_file:
            csv_data = await csv_file.read()
            csv_rows = csv_data.decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_rows)
            for row in csv_reader:
                # Extract data from each row
                average_daily_temperature = float(row['average_daily_temperature'])
                cumulative_daily_precipitation = float(row['cumulative_daily_precipitation'])
                relative_humidity = float(row['relative_humidity'])
                wind_speed = float(row['wind_speed'])
                wind_direction = row['wind_direction']
                total_solar_radiation = float(row['total_solar_radiation'])
                data_source = row.get('data_source', None)
                
                # Create new big agri data from CSV row
                data_dict = {
                    "average_daily_temperature": average_daily_temperature,
                    "cumulative_daily_precipitation": cumulative_daily_precipitation,
                    "relative_humidity": relative_humidity,
                    "wind_speed": wind_speed,
                    "wind_direction": wind_direction,
                    "total_solar_radiation": total_solar_radiation,
                    "data_source": data_source,
                }
          # # Check if data is coming from form fields as JSON object
        elif big_agri_form_data is not None:
            data_dict = big_agri_form_data.dict()
        else:
            raise HTTPException(status_code=400, detail="No data provided")

        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the AgriSenze to the agri_big_data collection
        doc_ref = agri_big_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = agri_big_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            agri_big_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            agri_big_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return bigAgriDataEntity(agri_big_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# # Get a specific Big Agri Data
# @bigAgriData.get("/big-agri-data/{agri_big_data_id}")
# async def find_agri_big_data(agri_big_data_id):
#     try:
#         doc = agri_big_data_ref.document(agri_big_data_id).get()
#         if doc.exists:
#             return {"agri_big_data": doc.to_dict()}
#         else:
#             raise HTTPException(status_code=404, detail="Geographic data not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Get all Big Agris data
# @bigAgriData.get('/big-agri-data')
# async def find_all_big_agris_data():
#     try:
#         agri_big_data = []
#         for doc in agri_big_data_ref.stream():
#             # Get the document ID
#             doc_id = doc.id
#             # Get the document data as a dictionary
#             doc_data = doc.to_dict()
#             # Create a new dictionary containing both the ID and data
#             combined_data = {"id": doc_id, **doc_data}
#             # Append the combined data to the list
#             agri_big_data.append(combined_data)        
#         return {"agri_big_data": agri_big_data}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

# # Create a new Big Agri Data        
# @bigAgriData.post('/big-agri-data')
# async def create_agri_big_data(geographic_id: str, agri_big_data: AgriBigData):
#     try:
#         # Check if the referenced geographic data exists in the database
#         geographic_document = geographic_data_ref.document(geographic_id).get()
#         if not geographic_document.exists:
#             raise HTTPException(status_code=404, detail="Geographic id not found")
#         # Convert bigAgriData object to dictionary
#         data_dict: Dict[str, Any] = agri_big_data.dict()
#         # Add the geographic_id to the data dictionary
#         data_dict["location_id"] = geographic_id
#         # Add the Big Agri Data to the agri_big_data collection
#         doc_ref = agri_big_data_ref.add(data_dict)
#         # Retrieve the inserted document using its ID
#         inserted_document = agri_big_data_ref.document(doc_ref[1].id).get()
#         if inserted_document.exists:
#             # Convert the inserted document to a dictionary
#             agri_big_data_dict = inserted_document.to_dict()
#             # Add the document ID to the dictionary
#             agri_big_data_dict["id"] = doc_ref[1].id
#             # Return the created Big Agri Data entity
#             return bigAgriDataEntity(agri_big_data_dict)
#         else:
#             raise HTTPException(status_code=404, detail="Inserted document not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Update an existing Big Agri Data
# @bigAgriData.put("/big-agri-data/{agri_big_data_id}")
# async def update_agri_big_data(agri_big_data_id: str, agri_big_data: AgriBigData):
#     try:
#         # Retrieve the existing document
#         agri_big_data_doc = agri_big_data_ref.document(agri_big_data_id).get()
#         if agri_big_data_doc.exists:
#             # Update the document with the new data
#             agri_big_data_ref.document(agri_big_data_id).set(agri_big_data.dict())
#             # Retrieve the inserted document using its ID
#             inserted_document = agri_big_data_ref.document(agri_big_data_id).get()
#             if inserted_document.exists:
#                 # Convert the inserted document to a dictionary
#                 agri_big_data_dict = inserted_document.to_dict()
#                 # Add the document ID to the dictionary
#                 agri_big_data_dict["id"] = agri_big_data_id
#                 # Return the created Big Agri Data entity
#                 return bigAgriDataEntity(agri_big_data_dict)
#             else:
#                 raise HTTPException(status_code=404, detail="Inserted Big Agri Data document not found")
#         else:
#             raise HTTPException(status_code=404, detail="Big Agri Data not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Delete an existing Big Agri Data
# @bigAgriData.delete("/big-agri-data/{agri_big_data_id}")
# async def delete_agri_big_data(agri_big_data_id):
#     try:
#         agri_big_data_ref.document(agri_big_data_id).delete()
#         return {"message": "Big Agri Data deleted successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))