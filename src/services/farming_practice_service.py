from ast import Dict
import csv
from datetime import datetime
import json
from typing import Optional
from fastapi import File, HTTPException, UploadFile
from common import constants
import requests
import pandas as pd
from models.agri_big_dataset import FarmingPracticeDataFeatures
# Initialize the expires and last_modified variables 
expire_time = None
last_modified = None
async def fetch_farming_practice_data_features(data_source_info: FarmingPracticeDataFeatures, location: Dict, referencetime: Dict):
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
                #TODO:
                pass
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again!")

async def upload_farming_practice_data_features(farming_practice_csv_file: Optional[UploadFile] = File(None)):
    try:        
        farming_practice_data_dict = {}        
        # Check if data is coming from a CSV file
        if farming_practice_csv_file:
            csv_data = await farming_practice_csv_file.read()
            csv_rows = csv_data.decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_rows)
            
            # Iterate over each row
            for idx, row in enumerate(csv_reader, start=1):
                # Check if any cell in the row has a non-empty value
                if any(cell.strip() != '' for cell in row.values()):
                    # Create a dictionary to hold data for each row
                    row_data = {}
                    for column_name, value in row.items():
                        # Add extracted data to the row dictionary
                        row_data[column_name] = value                
                    # Add the row data to the main dictionary using index as key
                    farming_practice_data_dict[idx] = row_data            
                # Return the data read from the CSV file
            farming_practice_data_from_file_dict = {str(key): value for key, value in farming_practice_data_dict.items()}
            return farming_practice_data_from_file_dict            
        else:
            farming_practice_data_from_file_dict ={}
            return farming_practice_data_from_file_dict
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong extracting the data from csv file. Please try again!")