import csv
from typing import Any, Dict, Optional
import bson
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import firebase_admin, db
from models.soil_data import SoilData
from bson import ObjectId
from schemas.soil_data_schema import soilDataEntity
import httpx

#========================================================
# Soil Data API End Points Router Implementation
#========================================================
soilData = APIRouter(tags=["Soil Data APIs"])

# Collection reference
soil_data_ref = db.collection("soil_data")
geographic_data_ref = db.collection("geographic_data")

# Get all soils data
@soilData.get('/soil-data')
async def find_all_soils_data():
    try:
        soil_data = []
        for doc in soil_data_ref.stream():
            # Get the document ID
            doc_id = doc.id
            # Get the document data as a dictionary
            doc_data = doc.to_dict()
            # Create a new dictionary containing both the ID and data
            combined_data = {"id": doc_id, **doc_data}
            # Append the combined data to the list
            soil_data.append(combined_data)        
        return {"soil_data": soil_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific Soil Data
@soilData.get("/soil-data/{soil_data_id}")
async def find_soil_data(soil_data_id):
    try:
        doc = soil_data_ref.document(soil_data_id).get()
        if doc.exists:
            return {"soil_data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Geographic data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new Soil Data        
@soilData.post('/soil-data')
async def create_soil_data(geographic_id: str, soil_data: SoilData):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")
        # Convert soilData object to dictionary
        data_dict: Dict[str, Any] = soil_data.dict()
        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the Soil Data to the soil_data collection
        doc_ref = soil_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = soil_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            soil_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            soil_data_dict["id"] = doc_ref[1].id
            # Return the created Soil Data entity
            return soilDataEntity(soil_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new AgriSenze data from data sources
@soilData.post('/upload-soil-data')
async def upload_soil_data(geographic_id: str, csv_file: Optional[UploadFile] = File(None), soil_form_data: Optional[Dict[str, Any]] = Form(None)):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")

        data_dict = {}
        
        # Check if data is coming from user input as JSON object or from any API services
        # if soil_data is not None:
        #     data_dict = soil_data.dict()

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
        elif soil_form_data is not None:
            data_dict = soil_form_data.dict()
        else:
            raise HTTPException(status_code=400, detail="No data provided")

        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the Soil data to the soil_data collection
        doc_ref = soil_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = soil_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            soil_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            soil_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return soilDataEntity(soil_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Update an existing Soil Data
@soilData.put("/soil-data/{soil_data_id}")
async def update_soil_data(soil_data_id: str, soil_data: SoilData):
    try:
        # Retrieve the existing document
        soil_data_doc = soil_data_ref.document(soil_data_id).get()
        if soil_data_doc.exists:
            # Update the document with the new data
            soil_data_ref.document(soil_data_id).set(soil_data.dict())
            # Retrieve the inserted document using its ID
            inserted_document = soil_data_ref.document(soil_data_id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                soil_data_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                soil_data_dict["id"] = soil_data_id
                # Return the created Soil Data entity
                return soilDataEntity(soil_data_dict)
            else:
                raise HTTPException(status_code=404, detail="Inserted Soil Data document not found")
        else:
            raise HTTPException(status_code=404, detail="Soil Data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete an existing Soil Data
@soilData.delete("/soil-data/{soil_data_id}")
async def delete_soil_data(soil_data_id):
    try:
        soil_data_ref.document(soil_data_id).delete()
        return {"message": "Soil Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))