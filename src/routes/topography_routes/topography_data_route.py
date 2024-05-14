import csv
from typing import Any, Dict, Optional
import bson
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import firebase_admin, db
from models.topography_data import TopographyData
from bson import ObjectId
from schemas.topography_data_schema import topographyDataEntity
import httpx

#========================================================
# Topography Data API End Points Router Implementation
#========================================================
topographyData = APIRouter(tags=["Topography Data APIs"])

# Collection reference
topography_data_ref = db.collection("topography_data")
geographic_data_ref = db.collection("geographic_data")

# Get all topographies data
@topographyData.get('/topography-data')
async def find_all_topographies_data():
    try:
        topography_data = []
        for doc in topography_data_ref.stream():
            # Get the document ID
            doc_id = doc.id
            # Get the document data as a dictionary
            doc_data = doc.to_dict()
            # Create a new dictionary containing both the ID and data
            combined_data = {"id": doc_id, **doc_data}
            # Append the combined data to the list
            topography_data.append(combined_data)        
        return {"topography_data": topography_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific Topography Data
@topographyData.get("/topography-data/{topography_data_id}")
async def find_topography_data(topography_data_id):
    try:
        doc = topography_data_ref.document(topography_data_id).get()
        if doc.exists:
            return {"topography_data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Geographic data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new Topography Data        
@topographyData.post('/topography-data')
async def create_topography_data(geographic_id: str, topography_data: TopographyData):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")
        # Convert topographyData object to dictionary
        data_dict: Dict[str, Any] = topography_data.dict()
        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the Topography Data to the topography_data collection
        doc_ref = topography_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = topography_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            topography_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            topography_data_dict["id"] = doc_ref[1].id
            # Return the created Topography Data entity
            return topographyDataEntity(topography_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new AgriSenze data from data sources
@topographyData.post('/upload-topography-data')
async def upload_topography_data(geographic_id: str, csv_file: Optional[UploadFile] = File(None), topography_form_data: Optional[Dict[str, Any]] = Form(None)):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")

        data_dict = {}
        # Check if data is coming from user input as JSON object or from any API services
        # if topography_data is not None:
        #     print('Comes to weather data object')
        #     data_dict = topography_data.dict()
        # Check if data is coming from a CSV file
        if csv_file:
            csv_data = await csv_file.read()
            csv_rows = csv_data.decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_rows)
            for row in csv_reader:
                # Extract data from each row
                aspect = float(row['aspect'])
                altitude = float(row['altitude'])
                topography_type = float(row['topography_type'])
                ground_area_coverage_km2 = float(row['ground_area_coverage_km2'])
                data_source = row.get('data_source', None)                
                # Create new agrisenze data from CSV row
                data_dict = {
                    "aspect": aspect,
                    "altitude": altitude,
                    "topography_type": topography_type,
                    "ground_area_coverage_km2": ground_area_coverage_km2,
                    "data_source": data_source,
                }
          # # Check if data is coming from form fields as JSON object
        elif topography_form_data is not None:
            data_dict = topography_form_data.dict()
        else:
            raise HTTPException(status_code=400, detail="No data provided")

        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the AgriSenze to the topography_data collection
        doc_ref = topography_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = topography_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            topography_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            topography_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return topographyDataEntity(topography_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Update an existing Topography Data
@topographyData.put("/topography-data/{topography_data_id}")
async def update_topography_data(topography_data_id: str, topography_data: TopographyData):
    try:
        # Retrieve the existing document
        topography_data_doc = topography_data_ref.document(topography_data_id).get()
        if topography_data_doc.exists:
            # Update the document with the new data
            topography_data_ref.document(topography_data_id).set(topography_data.dict())
            # Retrieve the inserted document using its ID
            inserted_document = topography_data_ref.document(topography_data_id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                topography_data_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                topography_data_dict["id"] = topography_data_id
                # Return the created Topography Data entity
                return topographyDataEntity(topography_data_dict)
            else:
                raise HTTPException(status_code=404, detail="Inserted Topography Data document not found")
        else:
            raise HTTPException(status_code=404, detail="Topography Data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete an existing Topography Data
@topographyData.delete("/topography-data/{topography_data_id}")
async def delete_topography_data(topography_data_id):
    try:
        topography_data_ref.document(topography_data_id).delete()
        return {"message": "Topography Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))