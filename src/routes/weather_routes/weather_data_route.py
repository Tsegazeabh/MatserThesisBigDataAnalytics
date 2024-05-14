import csv
from typing import Any, Dict, Optional
import bson
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import firebase_admin, db
from models.weather_data import WeatherData
from bson import ObjectId
from schemas.weather_data_schema import weatherDataEntity
import httpx

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
            raise HTTPException(status_code=404, detail="Geographic id not found")
        # Convert weatherData object to dictionary
        data_dict: Dict[str, Any] = weather_data.dict()
        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the Weather Data to the weather_data collection
        doc_ref = weather_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = weather_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            weather_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            weather_data_dict["id"] = doc_ref[1].id
            # Return the created Weather Data entity
            return weatherDataEntity(weather_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new weather data from data sources
@weatherData.post('/upload-weather-data')
async def upload_weather_data(geographic_id: str, csv_file: Optional[UploadFile] = File(None), weather_form_data: Optional[Dict[str, Any]] = Form(None)):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")
        data_dict = {}      
        # Check if data is coming from a CSV file
        if csv_file:
            csv_data = await csv_file.read()
            csv_rows = csv_data.decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_rows)
            for row in csv_reader:
                # Extract data from each row
                best_estimate_mean_air_temperature_P1M = float(row['best_estimate_mean_air_temperature_P1M'])
                best_estimate_sum_precipitation_amount_P1M = float(row['best_estimate_sum_precipitation_amount_P1M'])
                mean_relative_humidity_P1M = float(row['mean_relative_humidity_P1M'])
                mean_wind_speed_P1M = float(row['mean_wind_speed_P1M'])
                mean_surface_air_pressure_P1M = row['mean_surface_air_pressure_P1M']
                best_estimate_mean_air_temperature_P1D = float(row['best_estimate_mean_air_temperature_P1D'])
                best_estimate_sum_precipitation_amount_P1D = float(row['best_estimate_sum_precipitation_amount_P1D'])
                mean_relative_humidity_P1D = float(row['mean_relative_humidity_P1D'])
                mean_wind_speed_P1D = float(row['mean_wind_speed_P1D'])
                mean_surface_air_pressure_P1D = float(row['mean_surface_air_pressure_P1D'])
                data_source = row.get('data_source', None)
                
                # Create new weather data from CSV row
                data_dict = {
                    "best_estimate_mean_air_temperature_P1M": best_estimate_mean_air_temperature_P1M,
                    "best_estimate_sum_precipitation_amount_P1M": best_estimate_sum_precipitation_amount_P1M,
                    "mean_relative_humidity_P1M": mean_relative_humidity_P1M,
                    "mean_wind_speed_P1M": mean_wind_speed_P1M,
                    "mean_surface_air_pressure_P1M": mean_surface_air_pressure_P1M,
                    "best_estimate_mean_air_temperature_P1D": best_estimate_mean_air_temperature_P1D,
                    "best_estimate_sum_precipitation_amount_P1D":best_estimate_sum_precipitation_amount_P1D,
                    "mean_relative_humidity_P1D":mean_relative_humidity_P1D,
                    "mean_wind_speed_P1D":mean_wind_speed_P1D,
                    "mean_surface_air_pressure_P1D":mean_surface_air_pressure_P1D,
                    "data_source": data_source,
                }
          # # Check if data is coming from form fields as JSON object
        elif weather_form_data is not None:
            data_dict = weather_form_data.dict()
        else:
            raise HTTPException(status_code=400, detail="No data provided")

        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the AgriSenze to the weather_data collection
        doc_ref = weather_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = weather_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            weather_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            weather_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return weatherDataEntity(weather_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Update an existing Weather Data
@weatherData.put("/weather-data/{weather_data_id}")
async def update_weather_data(weather_data_id: str, weather_data: WeatherData):
    try:
        # Retrieve the existing document
        weather_data_doc = weather_data_ref.document(weather_data_id).get()
        if weather_data_doc.exists:
            # Update the document with the new data
            weather_data_ref.document(weather_data_id).set(weather_data.dict())
            # Retrieve the inserted document using its ID
            inserted_document = weather_data_ref.document(weather_data_id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                weather_data_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                weather_data_dict["id"] = weather_data_id
                # Return the created Weather Data entity
                return weatherDataEntity(weather_data_dict)
            else:
                raise HTTPException(status_code=404, detail="Inserted Weather Data document not found")
        else:
            raise HTTPException(status_code=404, detail="Weather Data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete an existing Weather Data
@weatherData.delete("/weather-data/{weather_data_id}")
async def delete_weather_data(weather_data_id):
    try:
        weather_data_ref.document(weather_data_id).delete()
        return {"message": "Weather Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))