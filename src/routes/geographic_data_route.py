import bson
from fastapi import APIRouter, HTTPException
from utils.firebase_storage import firebase_admin, db
from models.geographic_data import GeographicData
from bson import ObjectId
from schemas.geographic_data_schema import geographicDataEntity, geographicsDataEntity
import httpx
from typing import Any, Dict
from services import geographic_service

#========================================================
# geographic Data API End Points Router Implementation
#========================================================
geographicData = APIRouter(
    tags=["Geographic Data APIs"]
)
# Collection reference
geographic_data_ref = db.collection("geographic_data")

# Get all Geographic data
@geographicData.get('/geographic-data')
async def find_all_geographics_data():
    try:
        geographic_data = []
        for doc in geographic_data_ref.stream():
            # Get the document ID
            doc_id = doc.id
            # Get the document data as a dictionary
            doc_data = doc.to_dict()
            # Create a new dictionary containing both the ID and data
            combined_data = {"id": doc_id, **doc_data}
            # Append the combined data to the list
            geographic_data.append(combined_data)        
        return {"geographic_data": geographic_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific Geographic data
@geographicData.get("/geographic-data/{geographic_data_id}")
async def find_geographic_data(geographic_data_id):
    try:
        doc = geographic_data_ref.document(geographic_data_id).get()
        if doc.exists:
            return {"geographic_data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Geographic data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new Geographic data        
@geographicData.post('/geographic-data')
async def create_geographic_data(geographic_data: GeographicData):
    try:
        data_dict: Dict[str, Any] = geographic_data.dict()
        doc_ref = geographic_data_ref.add(data_dict)
        # Retrieve the inserted document using its id
        inserted_document = geographic_data_ref.document(doc_ref[1].id).get()        
        # Get the existing dictionary from Firestore document
        geographic_data= inserted_document.to_dict()
        # Get the document ID
        document_id = doc_ref[1].id
        # Update the dictionary with the 'id' key
        geographic_data["id"] = document_id
        if inserted_document:
            return geographicDataEntity(geographic_data)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update an existing Geographic data
@geographicData.put("/geographic-data/{geographic_data_id}")
async def update_geographic_data(geographic_data_id: str, geographic_data: GeographicData):
    try:
        # Convert GeographicData object to a dictionary
        geographic_data_dict = geographic_data.dict()        
        # Update the document in Firestore using the converted dictionary
        geographic_data_ref.document(geographic_data_id).set(geographic_data_dict, merge=True)        
        # Retrieve the updated document
        inserted_document = geographic_data_ref.document(geographic_data_id).get()        
        if inserted_document:
            # Get the updated data as a dictionary
            updated_data = inserted_document.to_dict()
            # Add the document ID to the dictionary
            updated_data["id"] = geographic_data_id
            return updated_data
        else:
            raise HTTPException(status_code=404, detail="Updated document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete an existing Geographic data
@geographicData.delete("/geographic-data/{geographic_data_id}")
async def delete_geographic_data(geographic_data_id):
    try:
        geographic_data_ref.document(geographic_data_id).delete()
        return {"message": "Geographic data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))