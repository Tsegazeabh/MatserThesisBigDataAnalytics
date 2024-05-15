import csv
from typing import Any, Dict
from fastapi import APIRouter, File, HTTPException, UploadFile
from utils.firebase_storage import db
from models.weather_data import WeatherData

#========================================================
# Weather Data API End Points Router Implementation
#========================================================
weatherData = APIRouter(tags=["Weather Data APIs"])

# Collection reference
weather_data_ref = db.collection("weather_data")
geographic_data_ref = db.collection("geographic_data")

# Get all weathers data
@weatherData.get('/weather-data')
async def find_all_weathers_data():
    try:
        weather_data = []
        for doc in weather_data_ref.stream():
            # Get the document ID
            doc_id = doc.id
            # Get the document data as a dictionary
            doc_data = doc.to_dict()
            # Create a new dictionary containing both the ID and data
            combined_data = {"id": doc_id, **doc_data}
            # Append the combined data to the list
            weather_data.append(combined_data)        
        return {"weather_data": weather_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific Weather Data
@weatherData.get("/weather-data/{weather_data_id}")
async def find_weather_data(weather_data_id):
    try:
        doc = weather_data_ref.document(weather_data_id).get()
        if doc.exists:
            return {"weather_data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Geographic data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new Weather Data        
@weatherData.post('/weather-data')
async def create_weather_data(geographic_id: str, weather_data: WeatherData):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=500, detail="Geographic id not found")
        # Convert weather data object to dictionary
        data_dict: Dict[str, Any] = weather_data.model_dump()
        # Add the geographic_id to the data dictionary
        data_dict_inserted = data_dict["data"]
        data_dict_inserted["geographic_id"] = geographic_id
        doc_ref = weather_data_ref.add(data_dict_inserted)
        inserted_document = weather_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            weather_data_dict = inserted_document.to_dict()
            weather_data_dict["id"] = doc_ref[1].id
            return weather_data_dict
        else:
            raise HTTPException(status_code=500, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again!")

# Create a new weather data from data sources
@weatherData.post('/upload-weather-data')
async def upload_weather_data(geographic_id: str, 
                              csv_file: UploadFile = File(..., media_type=["text/csv", "application/vnd.ms-excel"], description='Upload weather data from excel/csv file'), 
                              ):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=500, detail="Geographic Id not found")
        data_dict = {}
        weather_data_from_file_dict = {}      
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
                    weather_data_from_file_dict = row_data
                    # Add the geographic_id to the data dictionary
                    weather_data_from_file_dict["geographic_id"] = geographic_id
                    doc_ref = weather_data_ref.add(weather_data_from_file_dict)
                else:
                    raise HTTPException(status_code=500, detail="The file is empty. Please add some data to it!")   
        else:
            raise HTTPException(status_code=500, detail="No file selected. Please select excel/csv file and try again!")
        
        inserted_document = weather_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            return data_dict
        else:
            raise HTTPException(status_code=500, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong uploading the file to database. Please try again!")
    
# Update an existing Weather Data
@weatherData.put("/weather-data/{weather_data_id}", response_model=WeatherData)
async def update_weather_data(weather_data_id: str, weather_data: WeatherData):
    try:
        # Retrieve the existing document
        weather_data_doc = weather_data_ref.document(weather_data_id).get()        
        if weather_data_doc.exists:
            # Get the existing data from Firestore
            existing_data = weather_data_doc.to_dict()
            print('Existing Data: ', existing_data)
            for key, value in weather_data.model_dump().items():
                existing_data[key] = value
            # Set the updated data back to Firestore
            data_dict_updated = existing_data["data"]
            data_dict_updated["geographic_id"] = existing_data["geographic_id"]
            weather_data_ref.document(weather_data_id).set(data_dict_updated)
            data_dict_updated["id"] = weather_data_id
            return data_dict_updated
        else:
            raise HTTPException(status_code=500, detail="weather data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong updating the weather data selected. Please try again!")


# Delete an existing Weather Data
@weatherData.delete("/weather-data/{weather_data_id}")
async def delete_weather_data(weather_data_id):
    try:
        weather_data_ref.document(weather_data_id).delete()
        return {"message": "Weather Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))