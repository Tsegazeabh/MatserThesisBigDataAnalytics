import csv
from typing import Any, Dict, Optional
import bson
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import firebase_admin, db
from models.crop_data import CropData
from bson import ObjectId
from schemas.crop_data_schema import cropDataEntity
import httpx

#========================================================
# Crop Data API End Points Router Implementation
#========================================================
cropData = APIRouter(tags=["Crop Data APIs"])

# Collection reference
crop_data_ref = db.collection("crop_data")
geographic_data_ref = db.collection("geographic_data")

# Get all Crops data
@cropData.get('/crop-data')
async def find_all_crops_data():
    try:
        crop_data = []
        for doc in crop_data_ref.stream():
            # Get the document ID
            doc_id = doc.id
            # Get the document data as a dictionary
            doc_data = doc.to_dict()
            # Create a new dictionary containing both the ID and data
            combined_data = {"id": doc_id, **doc_data}
            # Append the combined data to the list
            crop_data.append(combined_data)        
        return {"crop_data": crop_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific Crop data
@cropData.get("/crop-data/{crop_data_id}")
async def find_crop_data(crop_data_id):
    try:
        doc = crop_data_ref.document(crop_data_id).get()
        if doc.exists:
            return {"crop_data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Geographic data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new Crop data        
@cropData.post('/crop-data')
async def create_crop_data(geographic_id: str, crop_data: CropData):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")
        # Convert CropData object to dictionary
        data_dict: Dict[str, Any] = crop_data.dict()
        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the crop data to the crop_data collection
        doc_ref = crop_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = crop_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            crop_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            crop_data_dict["id"] = doc_ref[1].id
            # Return the created crop data entity
            return cropDataEntity(crop_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new AgriSenze data from data sources
@cropData.post('/upload-crop-data')
async def upload_crop_data(geographic_id: str, csv_file: Optional[UploadFile] = File(None), crop_form_data: Optional[Dict[str, Any]] = Form(None)):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")

        data_dict = {}
        # Check if data is coming from user input as JSON object or from any API services
        # if crop_data is not None:
        #     print('Comes to weather data object')
        #     data_dict = crop_data.dict()
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
        elif crop_form_data is not None:
            data_dict = crop_form_data.dict()
        else:
            raise HTTPException(status_code=400, detail="No data provided")

        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the AgriSenze to the crop_data collection
        doc_ref = crop_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = crop_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            crop_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            crop_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return cropDataEntity(crop_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Update an existing Crop data
@cropData.put("/crop-data/{crop_data_id}")
async def update_crop_data(crop_data_id: str, crop_data: CropData):
    try:
        # Retrieve the existing document
        crop_data_doc = crop_data_ref.document(crop_data_id).get()
        if crop_data_doc.exists:
            # Update the document with the new data
            crop_data_ref.document(crop_data_id).set(crop_data.dict())
            # Retrieve the inserted document using its ID
            inserted_document = crop_data_ref.document(crop_data_id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                crop_data_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                crop_data_dict["id"] = crop_data_id
                # Return the created crop data entity
                return cropDataEntity(crop_data_dict)
            else:
                raise HTTPException(status_code=404, detail="Inserted crop data document not found")
        else:
            raise HTTPException(status_code=404, detail="Crop data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete an existing Crop data
@cropData.delete("/crop-data/{crop_data_id}")
async def delete_crop_data(crop_data_id):
    try:
        crop_data_ref.document(crop_data_id).delete()
        return {"message": "Crop data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))