import csv
from fastapi import APIRouter, File, HTTPException, UploadFile
from utils.firebase_storage import db

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
async def upload_agri_big_data(geographic_id: str, 
                           csv_file: UploadFile = File(..., media_type=["text/csv", "application/vnd.ms-excel"], description='Upload soil data from excel/csv file'), 
                           ):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=500, detail="Geographic Id not found")
        data_dict = {}
        big_agri_data_from_file_dict = {}      
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
                    big_agri_data_from_file_dict = row_data
                    # Add the geographic_id to the data dictionary
                    big_agri_data_from_file_dict["geographic_id"] = geographic_id
                    doc_ref = agri_big_data_ref.add(big_agri_data_from_file_dict)
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

    