from ast import Dict
import csv
from datetime import datetime
import json
import math
from typing import Optional
from fastapi import File, HTTPException, UploadFile
from common import constants as const
import requests
import pandas as pd
from models.agri_big_dataset import WeatherDataFeatures
from datetime import datetime, timezone
# Initialize the expires and last_modified variables 
expire_time = None
last_modified = None
async def fetch_weather_data_features(data_source_info: WeatherDataFeatures, location: Dict, referencetime: Dict):
    try:
        # If the request type http request with JSON response using RESTful APIs
        if data_source_info.request_type == "http":
                # If the data source is MET Norway
                if data_source_info.source == "MET_NO":                    
                    MET_client_id = const.MET_CLIENT_ID                    
                    parameters = const.MET_WEATHER_PARAMETERS                    
                    # If the location sepcified has a source weather station nearby
                    if location.get("nearby_source_station_id") is not None:
                        parameters["sources"] = location.get('nearby_source_station_id')                    
                    # If the weather features are selected by the user
                    if data_source_info.method == "select" and data_source_info.data_features is not None:
                        parameters["elements"] = ",".join(data_source_info.data_features.keys())  # Change here
                    else:
                        # Join the default weather features to create the elements param
                        parameters["elements"] = ",".join(const.DEFAULT_WEATHER_FEATURES)                      
                    if referencetime.get("from_date") is not None and referencetime.get("to_date") is not None:
                        parameters["referencetime"] = f"{referencetime.get('from_date')}/{referencetime.get('to_date')}"  # Change here
                    
                    MET_frost_url = const.MET_OBSERVATIONS_URL
                    # Issue an HTTP GET request to MET Norway
                    response = requests.get(MET_frost_url, parameters, auth=(MET_client_id,''))
                    # Check the response status code
                    if response.status_code == 200:
                        json_response = response.json()
                        data = json_response['data']
                        df = pd.DataFrame()
                        for i in range(len(data)):
                            row = pd.DataFrame(data[i]['observations'])
                            row['referenceTime'] = data[i]['referenceTime']
                            row['sourceId'] = data[i]['sourceId']
                            df_new = pd.DataFrame(row)
                            df = pd.concat([df, df_new], ignore_index=True)
                        excel_file_path = f"{const.STATIC_FILES_OUTPUT_PATH}/MET_weather_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
                       
                        # Save the DataFrame to Excel
                        df.to_excel(excel_file_path, index=True)  # Set index=True if you want to include row names in the Excel file
                        weather_data_features_json = df.to_json(orient="records")
                        # Parse the string into a list of dictionaries
                        data_list = json.loads(weather_data_features_json)
                        # Convert the list of dictionaries into a dictionary
                        weather_data_features = {str(index): item for index, item in enumerate(data_list)}
                        return weather_data_features
                    else:
                        raise HTTPException(response.status_code, detail="Error fetching weather data from MET Norway Frost API Service.")
                
                # If the data source is OPEN METEO, implement the service here
                elif data_source_info.source == "OPEN_METEO":
                    weather_data_features ={}
                    return weather_data_features
                
                # If the data source is METEOMATICS, implement the serivce here
                elif data_source_info.source == "METEOMATICS":
                    weather_data_features ={}
                    return weather_data_features
                 # If the data source is METEOMATICS, implement the serivce here
                elif data_source_info.source == "OPEN_WEATHER_MAP":
                    weather_data_features ={}
                     # If the weather features are selected by the user
                    if data_source_info.method == "select" and data_source_info.data_features is not None:
                        features = ",".join(data_source_info.data_features.keys())                    
                    # If the weather features are not selected, take the deafult features from settings
                    else:
                        # Join the default weather features to create the elements param
                        features = const.DEFAULT_OPEN_WEATHER_FEATURES                     
                    # Assuming 'referencetime.get("date")' returns a string in the format 'YYYY-MM-DD'
                    start_date_str = referencetime.get("from_date")
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    start_date_utc = start_date.replace(tzinfo=timezone.utc)
                    start_timestamp = int(start_date_utc.timestamp())

                    end_date_str = referencetime.get("to_date")
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    end_date_utc = end_date.replace(tzinfo=timezone.utc)
                    end_timestamp = int(end_date_utc.timestamp())

                    open_weather_history_url = f"{const.OPEN_WEATHER_HOSTORY_URL}?lat={location.get('latitude')}&lon={location.get('longitude')}&start={start_timestamp}&end={end_timestamp}&appid={const.OPEN_WEATHER_API_KEY}"
                    # Issue an HTTP GET request to MET Norway
                    response = requests.get(open_weather_history_url)
                    if response.status_code.code == 200:
                        json_data = response.json()
                        # Extract 'main', 'wind', and 'dt' objects and create a new JSON object
                        new_json_data = {}
                        for item in json_data['list']:
                            dt_value = item['dt']
                            main_data = item['main']
                            wind_data = item['wind']
                            # Create a new dictionary with user-defined features
                            new_json_data[dt_value] = {feature: main_data.get(feature, wind_data.get(feature)) for feature in features}
                        # Convert the new JSON object to a formatted string
                        weather_data_features = json.dumps(new_json_data, indent=4)
                    else:
                        raise HTTPException(response.status_code, detail="Error fetching weather data from open weathermap API Service.")
                    return weather_data_features                
                # If the data source is not defined return data source not valid message
                else:
                    raise HTTPException(status_code=500, detail="Data source is not valid")
        # If the request type from file features extraction
        else:
            if data_source_info.source == "MET_NO":
                pass
            else:
                pass
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again!")

async def upload_weather_data_features(weather_csv_file: Optional[UploadFile] = File(...)):
    try:        
        weather_data_dict = {}        
        # Check if data is coming from a CSV file
        if weather_csv_file:
            csv_data = await weather_csv_file.read()
            csv_rows = csv_data.decode('utf-8').splitlines()
            csv_reader = csv.DictReader(csv_rows)            
            # Iterate over each row
            for idx, row in enumerate(csv_reader, start=1):
                if any(cell.strip() != '' for cell in row.values()):
                    # Create a dictionary to hold data for each row
                    row_data = {}
                    for column_name, value in row.items():
                        # Add extracted data to the row dictionary
                        row_data[column_name] = value                
                    # Add the row data to the main dictionary using index as key
                    weather_data_dict[idx] = row_data            
            # Return the data read from the CSV file
            weather_data_from_file_dict = {str(key): value for key, value in weather_data_dict.items()}
            return weather_data_from_file_dict            
        else:
            weather_data_from_file_dict ={}
            return weather_data_from_file_dict             
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong extracting the data from csv file. Please try again!")

def calculate_pressure(P0, T, altitude):
    # constants
    g = 9.80665  # Acceleration due to gravity (m/s^2)
    M = 0.0289644  # Molar mass of Earth's air (kg/mol)
    R = 8.31432  # Universal gas constant (J/(mol*K))    
    # Calculate pressure
    pressure = P0 * math.exp((-g * M * altitude) / (R * (T + 273.15)))
    return pressure

async def fetch_meteorology_data_from_MET_No_frost(latitude, longitude, altitude):
    try:
        # Initialize the expires and last_modified variables 
        expire_time = None
        last_modified = None
        # Now let us fetch the meteorological forecast data from MET Norway
        request_url = f'{const.MET_FORECAST_URL}?lat={latitude}&lon={longitude}&altitude={altitude}'
        user_agent = const.MET_USER_AGENT
        # Define headers with User-Agent
        headers = {'User-Agent': user_agent, 'If-Modified-Since':last_modified}
        # Send HTTP GET request with headers
        response = requests.get(request_url, headers=headers)
        # Check the response status code
        if response.status_code == 200:
            # Save the expires and last_modified variables to avoid frequency request to the server
            expires_header = response.headers.get('expires')
            last_modified_header = response.headers.get('last-modified')
            # Convert expires and last_modified to RFC 1123 format
            expire_time = datetime.strptime(expires_header, '%a, %d %b %Y %H:%M:%S GMT').strftime('%a, %d %b %Y %H:%M:%S GMT')
            last_modified = datetime.strptime(last_modified_header, '%a, %d %b %Y %H:%M:%S GMT').strftime('%a, %d %b %Y %H:%M:%S GMT')
            weather_data = response.json()
            # Extract relevant information
            rows = []
            for entry in weather_data['properties']['timeseries']:
                instant_details = entry['data']['instant']['details']
                next_6_hours_details = entry['data'].get('next_6_hours', {}).get('details', None)
                row = {
                    'time': entry['time'],
                    'instant_air_temperature': instant_details['air_temperature'],
                    'instant_air_pressure_at_sea_level': instant_details['air_pressure_at_sea_level'],
                    'instant_relative_humidity': instant_details['relative_humidity'],
                    'next_6_hours_air_temperature_max': next_6_hours_details['air_temperature_max'] if next_6_hours_details else None,
                    'next_6_hours_air_temperature_min': next_6_hours_details['air_temperature_min'] if next_6_hours_details else None,
                    'next_6_hours_precipitation_amount': next_6_hours_details['precipitation_amount'] if next_6_hours_details else None
                }
                rows.append(row)

            # Create DataFrame
            MET_weather_df = pd.DataFrame(rows)
            MET_weather_df['time'] = pd.to_datetime(MET_weather_df['time'])
            # Add snow depth with zero values for testing during the summer season as there is no snow but should be automated for all seasons not part of the weather forecast
            MET_weather_df['snow_depth_cm'] = 0.0   
            # Group DataFrame by date
            grouped_df = MET_weather_df.groupby(MET_weather_df['time'].dt.date)
            # Calculate daily mean, min, max
            MET_daily_stats = grouped_df.agg(
                mean_air_temperature_2m=('instant_air_temperature', 'mean'),
                min_air_temperature_2m=('next_6_hours_air_temperature_min', 'min'),
                max_air_temperature_2m=('next_6_hours_air_temperature_max', 'max'),
                relative_humidity=('instant_relative_humidity', 'mean'),
                air_pressure_2m_mbar=('instant_air_pressure_at_sea_level', 'mean'),
                precipitation_mm=('next_6_hours_precipitation_amount', 'mean'),    
                snow_depth_cm=('snow_depth_cm', 'mean')
            )
            # calculate the air_pressure at certain altitude from the sea level air pressure forecast fetched from MET Norway
            MET_daily_stats['air_pressure_2m_mbar'] = MET_daily_stats.apply(lambda row: calculate_pressure(row['air_pressure_2m_mbar'], row['mean_air_temperature_2m'], altitude), axis=1)
            # Convert index to datetime
            MET_daily_stats.index = pd.to_datetime(MET_daily_stats.index)
            # Extract month and day from the index
            MET_daily_stats['month'] = MET_daily_stats.index.month
            MET_daily_stats['day'] = MET_daily_stats.index.day
            # Create test set for soil temperature at 2cm as ST_X_test
            ST2_X_test = MET_daily_stats
            return ST2_X_test
        else:
            # Request failed, print error message
            weather_data = {}
            raise HTTPException(status_code=response.status_code, detail='Error fetching from MET Norway')        
    except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))