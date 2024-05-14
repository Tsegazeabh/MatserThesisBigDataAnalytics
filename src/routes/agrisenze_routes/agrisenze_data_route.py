import csv
from typing import Any, Dict, Optional
import bson
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import firebase_admin, db
from models.agrisenze_data import AgriSenzeData
from bson import ObjectId
from schemas.agrisenze_data_schema import agrisenzeDataEntity
import httpx

#========================================================
# AgriSenze API End Points Router Implementation
#========================================================
agrisenzeData = APIRouter(tags=["AgriSenze APIs"])

# Collection reference
agrisenze_data_ref = db.collection("agrisenze_data")
geographic_data_ref = db.collection("geographic_data")

# Get all agrisenzes data
@agrisenzeData.get('/agrisenze-data')
async def find_all_agrisenzes_data():
    try:
        agrisenze_data = []
        for doc in agrisenze_data_ref.stream():
            # Get the document ID
            doc_id = doc.id
            # Get the document data as a dictionary
            doc_data = doc.to_dict()
            # Create a new dictionary containing both the ID and data
            combined_data = {"id": doc_id, **doc_data}
            # Append the combined data to the list
            agrisenze_data.append(combined_data)        
        return {"agrisenze_data": agrisenze_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific AgriSenze
@agrisenzeData.get("/agrisenze-data/{agrisenze_data_id}")
async def find_agrisenze_data(agrisenze_data_id):
    try:
        doc = agrisenze_data_ref.document(agrisenze_data_id).get()
        if doc.exists:
            return {"agrisenze_data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Geographic data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific agrisenze report
@agrisenzeData.get("/fetch-report/{project_id}/{report_id}")
async def fetch_agrisenze_data(project_id: str, report_id: str, report_name: str):
    url = f"https://feature-extraction-value-zu3hsmhdza-nw.a.run.app/api/v0/extractInfo/{project_id}/{report_id}"
    headers = {"report_name": report_name}
    # Make a GET request to the URL
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)        
        # Check if the request was successful
        if response.status_code == 200:
            print(response.json())
            return response.json()            
        else:
            # Raise an HTTPException if the request failed
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

# Create a new AgriSenze data from data sources       
@agrisenzeData.post('/create-agrisenze-data')
async def create_agrisenze_data(geographic_id: str, agrisenze_data: AgriSenzeData):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")
        # Convert agrisenzeData object to dictionary
        data_dict: Dict[str, Any] = agrisenze_data.dict()
        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the AgriSenze to the agrisenze_data collection
        doc_ref = agrisenze_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = agrisenze_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            agrisenze_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            agrisenze_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return agrisenzeDataEntity(agrisenze_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new AgriSenze data from data sources
@agrisenzeData.post('/upload-agrisenze-data')
async def upload_agrisenze_data(geographic_id: str, csv_file: Optional[UploadFile] = File(None), agrisenze_form_data: Optional[Dict[str, Any]] = Form(None)):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")

        data_dict = {}

        # Check if data is coming from user input as JSON object or from any API services
        # if agrisenze_data is not None:
        #     data_dict = agrisenze_data.dict()
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
        elif agrisenze_form_data is not None:
            data_dict = agrisenze_form_data.dict()
        else:
            raise HTTPException(status_code=400, detail="No data provided")

        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the AgriSenze to the agrisenze_data collection
        doc_ref = agrisenze_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = agrisenze_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            agrisenze_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            agrisenze_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return agrisenzeDataEntity(agrisenze_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Update an existing AgriSenze
@agrisenzeData.put("/agrisenze-data/{agrisenze_data_id}")
async def update_agrisenze_data(agrisenze_data_id, agrisenze_data: AgriSenzeData):
    try:
        # Retrieve the existing document
        agrisenze_data_doc = agrisenze_data_ref.document(agrisenze_data_id).get()
        if agrisenze_data_doc.exists:
            # Update the document with the new data
            agrisenze_data_ref.document(agrisenze_data_id).set(agrisenze_data.dict())
            # Retrieve the inserted document using its ID
            inserted_document = agrisenze_data_ref.document(agrisenze_data_id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                agrisenze_data_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                agrisenze_data_dict["id"] = agrisenze_data_id
                # Return the created AgriSenze entity
                return agrisenzeDataEntity(agrisenze_data_dict)
            else:
                raise HTTPException(status_code=404, detail="Inserted AgriSenze document not found")
        else:
            raise HTTPException(status_code=404, detail="AgriSenze data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete an existing AgriSenze
@agrisenzeData.delete("/agrisenze-data/{agrisenze_data_id}")
async def delete_agrisenze_data(agrisenze_data_id):
    try:
        agrisenze_data_ref.document(agrisenze_data_id).delete()
        return {"message": "AgriSenze data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))