import csv
from typing import Any, Dict
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import db
from models.soil_data import SoilData

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
            raise HTTPException(status_code=500, detail="Geographic id not found")
        # Convert soil data object to dictionary
        data_dict: Dict[str, Any] = soil_data.model_dump()
        # Add the geographic_id to the data dictionary
        data_dict_inserted = data_dict["data"]
        data_dict_inserted["geographic_id"] = geographic_id
        doc_ref = soil_data_ref.add(data_dict_inserted)
        inserted_document = soil_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            soil_data_dict = inserted_document.to_dict()
            soil_data_dict["id"] = doc_ref[1].id
            return soil_data_dict
        else:
            raise HTTPException(status_code=500, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again!")

# Create a new AgriSenze data from data sources
@soilData.post('/upload-soil-data')
async def upload_soil_data(geographic_id: str, 
                           csv_file: UploadFile = File(..., media_type=["text/csv", "application/vnd.ms-excel"], description='Upload soil data from excel/csv file'), 
                           ):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=500, detail="Geographic Id not found")
        data_dict = {}
        soil_data_from_file_dict = {}      
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
                    soil_data_from_file_dict = row_data
                    # Add the geographic_id to the data dictionary
                    soil_data_from_file_dict["geographic_id"] = geographic_id
                    doc_ref = soil_data_ref.add(soil_data_from_file_dict)
                else:
                    raise HTTPException(status_code=500, detail="The file is empty. Please add some data to it!")   
        else:
            raise HTTPException(status_code=500, detail="No file selected. Please select excel/csv file and try again!")
        
        inserted_document = soil_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            return data_dict
        else:
            raise HTTPException(status_code=500, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong uploading the file to database. Please try again!")


# Update an existing Soil Data
@soilData.put("/soil-data/{soil_data_id}", response_model = SoilData)
async def update_soil_data(soil_data_id: str, soil_data: SoilData):
    try:
        # Retrieve the existing document
        soil_data_doc = soil_data_ref.document(soil_data_id).get()        
        if soil_data_doc.exists:
            # Get the existing data from Firestore
            existing_data = soil_data_doc.to_dict()
            print('Existing Data: ', existing_data)
            for key, value in soil_data.model_dump().items():
                existing_data[key] = value
            # Set the updated data back to Firestore
            data_dict_updated = existing_data["data"]
            data_dict_updated["geographic_id"] = existing_data["geographic_id"]
            soil_data_ref.document(soil_data_id).set(data_dict_updated)
            data_dict_updated["id"] = soil_data_id
            return data_dict_updated
        else:
            raise HTTPException(status_code=500, detail="soil data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong updating the soil data selected. Please try again!")


# Delete an existing Soil Data
@soilData.delete("/soil-data/{soil_data_id}")
async def delete_soil_data(soil_data_id):
    try:
        soil_data_ref.document(soil_data_id).delete()
        return {"message": "Soil Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))