import csv
from typing import Any, Dict, Optional
import bson
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from utils.firebase_storage import firebase_admin, db
from models.IoT_sensors_data import IoTSensorsData
from bson import ObjectId
from schemas.IoT_sensors_data_schema import IoTSensorDataEntity
import httpx

#========================================================
# IoT Sensors Data API End Points Router Implementation
#========================================================
IoT_sensors_Data = APIRouter(tags=["IoT Sensors Data APIs"])

# Collection reference
IoT_sensors_data_ref = db.collection("IoT_sensors_data")
geographic_data_ref = db.collection("geographic_data")

# Get all IoT_sensors data
@IoT_sensors_Data.get('/IoT-sensors-data')
async def find_all_IoT_sensors_data():
    try:
        IoT_sensors_data = []
        for doc in IoT_sensors_data_ref.stream():
            # Get the document ID
            doc_id = doc.id
            # Get the document data as a dictionary
            doc_data = doc.to_dict()
            # Create a new dictionary containing both the ID and data
            combined_data = {"id": doc_id, **doc_data}
            # Append the combined data to the list
            IoT_sensors_data.append(combined_data)        
        return {"IoT_sensors_data": IoT_sensors_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific IoT Sensors Data
@IoT_sensors_Data.get("/IoT-sensors-data/{IoT_sensors_data_id}")
async def find_IoT_sensors_data(IoT_sensors_data_id):
    try:
        doc = IoT_sensors_data_ref.document(IoT_sensors_data_id).get()
        if doc.exists:
            return {"IoT_sensors_data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Geographic data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new IoT Sensors Data        
@IoT_sensors_Data.post('/IoT-sensors-data')
async def create_IoT_sensors_data(geographic_id: str, IoT_sensors_data: IoTSensorsData):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")
        # Convert IoTSensorsData object to dictionary
        data_dict: Dict[str, Any] = IoT_sensors_data.dict()
        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the IoT Sensors Data to the IoT_sensors_data collection
        doc_ref = IoT_sensors_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = IoT_sensors_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            IoT_sensors_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            IoT_sensors_data_dict["id"] = doc_ref[1].id
            # Return the created IoT Sensors Data entity
            return IoTSensorDataEntity(IoT_sensors_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create a new IoT Sensors data from data sources
@IoT_sensors_Data.post('/upload-IoT-sensors-data')
async def upload_IoT_sensors_data(geographic_id: str, csv_file: Optional[UploadFile] = File(None), IoT_sensors_form_data: Optional[Dict[str, Any]] = Form(None)):
    try:
        # Check if the referenced geographic data exists in the database
        geographic_document = geographic_data_ref.document(geographic_id).get()
        if not geographic_document.exists:
            raise HTTPException(status_code=404, detail="Geographic id not found")

        data_dict = {}
        # Check if data is coming from user input as JSON object or from any API services
        # if IoTSensors_data is not None:
        #     print('Comes to IoTSensors data object')
        #     data_dict = IoTSensors_data.dict()
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
        elif IoT_sensors_form_data is not None:
            data_dict = IoT_sensors_form_data.dict()
        else:
            raise HTTPException(status_code=400, detail="No data provided")

        # Add the geographic_id to the data dictionary
        data_dict["geographic_id"] = geographic_id
        # Add the AgriSenze to the IoTSensors_data collection
        doc_ref = IoT_sensors_data_ref.add(data_dict)
        # Retrieve the inserted document using its ID
        inserted_document = IoT_sensors_data_ref.document(doc_ref[1].id).get()
        if inserted_document.exists:
            # Convert the inserted document to a dictionary
            IoTSensors_data_dict = inserted_document.to_dict()
            # Add the document ID to the dictionary
            IoTSensors_data_dict["id"] = doc_ref[1].id
            # Return the created AgriSenze entity
            return IoTSensorDataEntity(IoTSensors_data_dict)
        else:
            raise HTTPException(status_code=404, detail="Inserted document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Update an existing IoT Sensors Data
@IoT_sensors_Data.put("/IoT-sensors-data/{IoT_sensors_data_id}")
async def update_IoT_sensors_data(IoT_sensors_data_id: str, IoT_sensors_data: IoTSensorsData):
    try:
        # Retrieve the existing document
        IoT_sensors_data_doc = IoT_sensors_data_ref.document(IoT_sensors_data_id).get()
        if IoT_sensors_data_doc.exists:
            # Update the document with the new data
            IoT_sensors_data_ref.document(IoT_sensors_data_id).set(IoT_sensors_data.dict())
            # Retrieve the inserted document using its ID
            inserted_document = IoT_sensors_data_ref.document(IoT_sensors_data_id).get()
            if inserted_document.exists:
                # Convert the inserted document to a dictionary
                IoT_sensors_data_dict = inserted_document.to_dict()
                # Add the document ID to the dictionary
                IoT_sensors_data_dict["id"] = IoT_sensors_data_id
                # Return the created IoT Sensors Data entity
                return IoTSensorDataEntity(IoT_sensors_data_dict)
            else:
                raise HTTPException(status_code=404, detail="Inserted IoT Sensors Data document not found")
        else:
            raise HTTPException(status_code=404, detail="IoT Sensors Data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete an existing IoT Sensors Data
@IoT_sensors_Data.delete("/IoT-sensors-data/{IoT_sensors_data_id}")
async def delete_IoT_sensors_data(IoT_sensors_data_id):
    try:
        IoT_sensors_data_ref.document(IoT_sensors_data_id).delete()
        return {"message": "IoT Sensors Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))