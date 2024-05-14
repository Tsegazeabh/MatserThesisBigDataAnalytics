from ast import Dict
import csv
from datetime import datetime
import json
from typing import Optional
from fastapi import File, HTTPException, UploadFile
import numpy as np
from common import constants
import requests
import pandas as pd
from models.agri_big_dataset import SoilDataFeatures
# Initialize the expires and last_modified variables 
expire_time = None
last_modified = None
async def fetch_soil_data_features(data_source_info: SoilDataFeatures, location: Dict):
    try:
        print(data_source_info)
        #  If the request type http request with JSON response using RESTful APIs
        if data_source_info.request_type == "http":
                print("Reached 00")
                if data_source_info.source == "ISRIC":                    
                    # Define query string for soil history data fetching 
                    print("Reached 000 ISRIC")          
                    longitude = location.get("longitude") if location.get("longitude") is not None else 10.7818
                    latitude = location.get("latitude") if location.get("latitude") is not None else 59.6605
                    print("Reached here 000 Location")
                    # If the method of selection is default, the default soil parameters are selected
                    if data_source_info.method == 'default':
                        data_source_info.depth = constants.DEFAULT_SOIL_FEATURES["depth"]
                        data_source_info.value = constants.DEFAULT_SOIL_FEATURES["value"]
                        data_source_info.data_features = constants.DEFAULT_SOIL_FEATURES["data_features"]
                  
                    query_string = build_soils_grid_query_string(data_source_info)
                    print("Reached here 000 Query string")
                    ISRIC_soil_grids_url = constants.ISRIC_SOILGRIDS_URL
                    print("Reached here 0000")
                     # make request to properties endpoint
                    response = requests.get(f"{ISRIC_soil_grids_url}?lon={longitude}&lat={latitude}&{query_string}") 
                    print("Reached here 00000")
                    print(response)
                    # Check the response status code
                    if response.status_code == 200:
                        print("Response successful")
                        # parse response
                        data = response.json()
                        print("Response Data:", data)
                        # continue with your application logic...
                        # Extracting data
                        columns = []
                        values = []
                        for layer in data['properties']['layers']:
                            layer_name = layer['name']
                            for depth in layer['depths']:
                                column_name = f"{layer_name}_{depth['label']} ({layer['unit_measure']['target_units']})"
                                columns.append(column_name)
                        for key in data['properties']['layers'][0]['depths'][0]['values']:
                            values.append(key)
                        # values = ['mean', 'uncertainty', 'Q0.05', 'Q0.5','Q0.95']
                        print("Column names:", columns)
                        print("values index:", values)
                        # Calculate the total number of depths
                        total_depths = sum(len(layer['depths']) for layer in data['properties']['layers'])
                        # Construct the data_matrix
                        data_matrix = np.zeros((len(values), total_depths), dtype=float)
                        # Populate the data_matrix
                        current_column_index = 0
                        print("Reched here layer")
                        for i, layer in enumerate(data['properties']['layers']):
                            for j, depth in enumerate(layer['depths']):
                                # Check for existence of the values in the data object returned
                                # mean = depth['values']['mean']/layer['unit_measure']['d_factor'] if 'mean' in depth['values'] else np.nan # This divides the mapped value by the conversion factor to get the target value
                                # uncertainty = depth['values']['uncertainty']/layer['unit_measure']['d_factor'] if 'uncertainty' in depth['values'] else np.nan
                                # q0_05 = depth['values']['Q0.05']/layer['unit_measure']['d_factor'] if 'Q0.05' in depth['values'] else np.nan
                                # q0_5 = depth['values']['Q0.5']/layer['unit_measure']['d_factor'] if 'Q0.5' in depth['values'] else np.nan
                                # q0_95 = depth['values']['Q0.95']/layer['unit_measure']['d_factor'] if 'Q0.95' in depth['values'] else np.nan
                                for idx, value in enumerate(values):
                                    data_matrix[idx, current_column_index] = depth['values'][value]/layer['unit_measure']['d_factor'] if value in depth['values'] else np.nan # This divides the mapped value by the conversion factor to get the target value
                                current_column_index += 1  # Move to the next column
                        # Constructing DataFrame
                        df = pd.DataFrame(data_matrix, index=values, columns=columns)
                        print("DF:", df)
                        # Define the file path where you want to save the Excel file
                        date_now = datetime.now()
                        excel_file_path = f"src/files/data/outputs/ISRIC_soil_properties_{date_now.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
                        print("Excel file entry")
                        # Save the DataFrame to Excel                        
                        print("Excel file generated success")
                        transposed_df = df.transpose()
                        transposed_df.to_excel(excel_file_path, index=True)  # Set index=True if you want to include row names in the Excel file
                        #soil_data_features = transposed_df.to_json(orient="records")
                        print("Transposed DF", transposed_df)
                        
                        # Iterate over the columns of the DataFrame
                        json_data = {}
                        for column in df.columns:
                            column_data = {}                            
                            for row in values:
                                # Extract values for the current column and statistic
                                value = df[column][row] if row in df[column] else np.nan
                                column_data[row] = value                            
                            # Add the column data to the JSON object
                            json_data[column] = column_data  
                        
                        # Convert the dictionary to JSON format
                        soil_data_features = json_data
                        print("Soil data features:", soil_data_features)
                        return soil_data_features
                    else:
                        print('Reached 2')
                        raise HTTPException(response.status_code, detail="Error fetching soil data from MET Norway Frost API Service.")
                elif data_source_info.source == "HWSD":
                    soil_data_features ={}
                    return soil_data_features
                elif data_source_info.source == "NMBU":
                    soil_data_features ={}
                    return soil_data_features
                else:
                    print('Reached 3')
                    raise HTTPException(status_code=500, detail="Data source is not valid")
        # If the request type from file features extraction
        else:
            if data_source_info.source == "MET_NO":
                pass
            else:
                pass
    except Exception as e:
        print('Reached 4 in soil')
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

# Define a function that takes data_features of soil grid object and returns the query string required for the request
def build_soils_grid_query_string(soil_data_info: SoilDataFeatures):
    query_string = ''
    print(soil_data_info.data_features.keys)
    # Extract properties
    properties = soil_data_info.data_features.keys()
    print(properties)
    for prop in properties:
        query_string += f'property={prop}&'

    # Extract depths
    depths = soil_data_info.depth
    print(depths)
    for depth in depths:
        query_string += f'depth={depth}&'

    # Extract values
    values = soil_data_info.value
    print(values)
    for value in values:
        query_string += f'value={value}&'

    # Remove the last '&' if present
    if query_string.endswith('&'):
        query_string = query_string[:-1] 
    print(query_string)
    return query_string

async def upload_soil_data_features(soil_csv_file: Optional[UploadFile] = File(None)):
    try:
        
        soil_data_dict = {}        
        # Check if data is coming from a CSV file
        if soil_csv_file:
            csv_data = await soil_csv_file.read()
            csv_rows = csv_data.decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_rows)
            
            # Iterate over each row
            for idx, row in enumerate(csv_reader, start=1):
                # Create a dictionary to hold data for each row
                row_data = {}
                for column_name, value in row.items():
                    # Add extracted data to the row dictionary
                    row_data[column_name] = value
                
                # Add the row data to the main dictionary using index as key
                soil_data_dict[idx] = row_data   
            soil_data_from_file_dict = {str(key): value for key, value in soil_data_dict.items()}         
            # Return the data read from the CSV file
            return soil_data_from_file_dict
            
        else:
            soil_data_from_file_dict ={}
            return soil_data_from_file_dict
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
""""
## ISRIC Soil Properties
    "bulk_density ":"cg/cm³",
    "cation_exchange_capacity ":"mmol(c)/kg",
    "volumetric_fraction_coarse_fragments_2m":"cm3/dm3",
    "clay_proportion":"g/kg",
    "total_nitrogen":"cg/kg",
    "soil_ph":"pH",
    "sand_proportion":"g/kg",
    "silt_proportion":"g/kg",        
    "soil_organic_carbon":"dg/kg",
    "organic_carbon_density":"hg/m³",
    "organic_carbon_stocks":"t/ha",
    "Volumetric Water Content at -1000 kPa (Field Capacity)":"cm³/cm³",
    "Volumetric Water Content at -330 kPa (Permanent Wilting Point)":"cm³/cm³",
    "Volumetric Water Content at -1500 kPa (Saturation)":"cm³/cm³",
"""
