import csv
from typing import Any, Dict
from fastapi import APIRouter, File, HTTPException, UploadFile
from utils.firebase_storage import db
from models.agrisenze_data import AgriSenzeData
import httpx
from common import constants as const


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
            doc_data = doc.to_dict()
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
    url = f"{const.ZP_REPORT_FETCHING_URL}/{project_id}/{report_id}"
    headers = {"report_name": report_name}
    # Make a GET request to the URL
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()            
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch report data from Djuli")

# Create a new AgriSenze data from data sources       
@agrisenzeData.post('/create-agrisenze-data')
async def create_agrisenze_data(geographic_id: str, agrisenze_data: AgriSenzeData):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=500, detail="Geographic id not found")
        # Convert agrisenzeData object to dictionary
        data_dict: Dict[str, Any] = agrisenze_data.model_dump()
        # Add the geographic_id to the data dictionary        
        print('Data Dict:', data_dict)
        data_dict_inserted = data_dict["data"]
        data_dict_inserted["geographic_id"] = geographic_id
        doc_ref = agrisenze_data_ref.add(data_dict_inserted)
        inserted_document = agrisenze_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            agrisenze_data_dict = inserted_document.to_dict()
            agrisenze_data_dict["id"] = doc_ref[1].id
            return agrisenze_data_dict
        else:
            raise HTTPException(status_code=500, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again!")

# Create a new AgriSenze data from data sources
@agrisenzeData.post('/upload-agrisenze-data')
async def upload_agrisenze_data(geographic_id: str, 
                                csv_file: UploadFile = File(..., media_type=["text/csv", "application/vnd.ms-excel"], description='Upload agrisenze data from excel/csv file'), 
                                ):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=500, detail="Geographic Id not found")
        data_dict = {}
        agrisenze_data_from_file_dict = {}      
        # Check if data is coming from a CSV file
        if csv_file:
            csv_data = await csv_file.read()
            csv_rows = csv_data.decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_rows)            
            # Iterate over each row
            for idx, row in enumerate(csv_reader, start=1):
                if any(cell.strip() != '' for cell in row.values()):
                    row_data = {}
                    for column_name, value in row.items():
                        row_data[column_name] = value                    
                    # Add the row data to the main dictionary using index as key
                    data_dict[idx] = row_data 
                    agrisenze_data_from_file_dict = row_data
                    # Add the geographic_id to the data dictionary
                    agrisenze_data_from_file_dict["geographic_id"] = geographic_id
                    doc_ref = agrisenze_data_ref.add(agrisenze_data_from_file_dict)
                else:
                    raise HTTPException(status_code=500, detail="The file is empty. Please add some data to it!")   
        else:
            raise HTTPException(status_code=500, detail="No file selected. Please select excel/csv file and try again!")
        
        inserted_document = agrisenze_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            return data_dict
        else:
            raise HTTPException(status_code=500, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong uploading the file to database. Please try again!")
    
# Update an existing AgriSenze
@agrisenzeData.put("/agrisenze-data/{agrisenze_data_id}", response_model=AgriSenzeData)
async def update_agrisenze_data(agrisenze_data_id, agrisenze_data: AgriSenzeData):
    try:
       # Retrieve the existing document
       agrisenze_data_doc = agrisenze_data_ref.document(agrisenze_data_id).get()        
       if agrisenze_data_doc.exists:
           # Get the existing data from Firestore
           existing_data = agrisenze_data_doc.to_dict()
           print('Existing Data: ', existing_data)
           for key, value in agrisenze_data.model_dump().items():
               existing_data[key] = value
           # Set the updated data back to Firestore
           data_dict_updated = existing_data["data"]
           data_dict_updated["geographic_id"] = existing_data["geographic_id"]
           agrisenze_data_ref.document(agrisenze_data_id).set(data_dict_updated)
           data_dict_updated["id"] = agrisenze_data_id
           return data_dict_updated
       else:
           raise HTTPException(status_code=500, detail="agrisenze data not found")
    except Exception as e:
       raise HTTPException(status_code=500, detail="Something went wrong updating theagrisenze data selected. Please try again!")

# Delete an existing AgriSenze
@agrisenzeData.delete("/agrisenze-data/{agrisenze_data_id}")
async def delete_agrisenze_data(agrisenze_data_id):
    try:
        agrisenze_data_ref.document(agrisenze_data_id).delete()
        return {"message": "AgriSenze data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))