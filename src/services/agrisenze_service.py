from ast import Dict
import csv
from datetime import datetime
import json
from typing import Optional
from fastapi import File, HTTPException, UploadFile
from common import constants
import requests
import pandas as pd
from models.agri_big_dataset import AgrisenzeDataFeatures
# Initialize the expires and last_modified variables 
expire_time = None
last_modified = None
async def fetch_agrisenze_data_features(data_source_info: AgrisenzeDataFeatures, location: Dict, referencetime: Dict):
    try:
        # If the request type http request with JSON response using RESTful APIs
        if data_source_info.request_type == "http":
            if data_source_info.source == "DJULI": 
                #TODO:                   
                pass
        else:
            if data_source_info.source == "DJULI":
                #TODO:
                pass
            else:
                pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def upload_agrisenze_data_features(agrisenze_csv_file: Optional[UploadFile] = File(None)):
    try:
        
        agrisenze_data_dict = {}        
        # Check if data is coming from a CSV file
        if agrisenze_csv_file:
            csv_data = await agrisenze_csv_file.read()
            csv_rows = csv_data.decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_rows)            
            # Iterate over each row
            for idx, row in enumerate(csv_reader, start=1):
                if any(cell.strip() != '' for cell in row.values()):
                    row_data = {}
                    for column_name, value in row.items():
                        row_data[column_name] = value                    
                    # Add the row data to the main dictionary using index as key
                    agrisenze_data_dict[idx] = row_data            
                # Return the data read from the CSV file
            agrisenze_data_from_file_dict = {str(key): value for key, value in agrisenze_data_dict.items()}
            return agrisenze_data_from_file_dict            
        else:
            agrisenze_data_from_file_dict ={}
            return agrisenze_data_from_file_dict
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong extracting the data from csv file. Please try again!")