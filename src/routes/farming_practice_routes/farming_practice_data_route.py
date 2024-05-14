import csv
from typing import Any, Dict, Optional
import bson
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import firebase_admin, db
from models.farming_practice_data import FarmingPracticeData
from bson import ObjectId
from schemas.farming_practice_data_schema import farmingPracticeDataEntity
import httpx

#========================================================
# Farming practice API End Points Router Implementation
#========================================================
farmingPracticeData = APIRouter(tags=["Farming practice APIs"])

# Collection reference
farming_practice_data_ref = db.collection("farming_practice_data")
geographic_data_ref = db.collection("geographic_data")

# Get all Farming practice
@farmingPracticeData.get('/farming-practice')
async def find_all_farming_practices_data():
    try:
        farming_practice_data = []
        for doc in farming_practice_data_ref.stream():
            # Get the document ID
            doc_id = doc.id
            # Get the document data as a dictionary
            doc_data = doc.to_dict()
            # Create a new dictionary containing both the ID and data
            combined_data = {"id": doc_id, **doc_data}
            # Append the combined data to the list
            farming_practice_data.append(combined_data)        
        return {"farming_practice_data": farming_practice_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific Farming practice
@farmingPracticeData.get("/farming-practice/{farming_practice_data_id}")
async def find_farming_practice_data(farming_practice_data_id):
    try:
        doc = farming_practice_data_ref.document(farming_practice_data_id).get()
        if doc.exists:
            return {"farming_practice_data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Geographic data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific Farming practice report
# @farmingPracticeData.get("/fetch-report/{project_id}/{report_id}")
# async def fetch_farming_practice_data(project_id: str, report_id: str, report_name: str):
#     url = f"https://feature-extraction-value-zu3hsmhdza-nw.a.run.app/api/v0/extractInfo/{project_id}/{report_id}"
#     headers = {"report_name": report_name}
#     # Make a GET request to the URL
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers)        
#         # Check if the request was successful
#         if response.status_code == 200:
#             print(response.json())
#             return response.json()            
#         else:
#             # Raise an HTTPException if the request failed
#             raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

# Create a new Farming practice        
@farmingPracticeData.post('/farming-practice')
async def create_farming_practice_data(geographic_id: str, farming_practice_data: FarmingPracticeData):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")
        # Convert farmingPracticeData object to dictionary
        data_dict: Dict[str, Any] = farming_practice_data.dict()
        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the Farming practice to the farming_practice_data collection
        doc_ref = farming_practice_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = farming_practice_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            farming_practice_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            farming_practice_data_dict["id"] = doc_ref[1].id
            # Return the created Farming practice entity
            return farmingPracticeDataEntity(farming_practice_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new AgriSenze data from data sources
@farmingPracticeData.post('/upload-farming-practice-data')
async def upload_farming_practice_data(geographic_id: str, csv_file: Optional[UploadFile] = File(None), farming_practice_form_data: Optional[Dict[str, Any]] = Form(None)):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")

        data_dict = {}
        # Check if data is coming from user input as JSON object or from any API services
        # if farming_practice_data is not None:
        #     print('Comes to farming_practice data object')
        #     data_dict = farming_practice_data.dict()
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
                
                # Create new agrisenze data from CSV row
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
        elif farming_practice_form_data is not None:
            data_dict = farming_practice_form_data.dict()
        else:
            raise HTTPException(status_code=400, detail="No data provided")

        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the AgriSenze to the farming_practice_data collection
        doc_ref = farming_practice_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = farming_practice_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            farming_practice_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            farming_practice_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return farmingPracticeDataEntity(farming_practice_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Update an existing Farming practice
@farmingPracticeData.put("/farming-practice/{farming_practice_data_id}")
async def update_farming_practice_data(farming_practice_data_id, farming_practice_data: FarmingPracticeData):
    try:
        # Retrieve the existing document
        farming_practice_data_doc = farming_practice_data_ref.document(farming_practice_data_id).get()
        if farming_practice_data_doc.exists:
            # Update the document with the new data
            farming_practice_data_ref.document(farming_practice_data_id).set(farming_practice_data.dict())
            # Retrieve the inserted document using its ID
            inserted_document = farming_practice_data_ref.document(farming_practice_data_id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                farming_practice_data_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                farming_practice_data_dict["id"] = farming_practice_data_id
                # Return the created Farming practice entity
                return farmingPracticeDataEntity(farming_practice_data_dict)
            else:
                raise HTTPException(status_code=404, detail="Inserted Farming practice document not found")
        else:
            raise HTTPException(status_code=404, detail="Farming practice not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete an existing Farming practice
@farmingPracticeData.delete("/farming-practice/{farming_practice_data_id}")
async def delete_farming_practice_data(farming_practice_data_id):
    try:
        farming_practice_data_ref.document(farming_practice_data_id).delete()
        return {"message": "Farming practice deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))