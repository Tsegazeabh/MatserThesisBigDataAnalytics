from datetime import datetime
import os
import re
from fastapi import APIRouter,Form, HTTPException
import pandas as pd
from joblib import load
from models.data_source_options_model import SoilTempDataSources
from services.weather_service import fetch_meteorology_data_from_MET_No_frost

# Define FastAPI app
predictTarget = APIRouter(tags=["ML Based Soil Temperature Prediction Models' APIs"])

# Prediction endpoint
@predictTarget.post("/predictSoilTemperature")
async def predict_target(latitude:float = Form(..., description='Enter latitude with less than or equal to 4 decimal points'), 
                         longitude:float = Form(..., description='Enter longitude with less than or equal to 4 decimal points'), 
                         altitude:int = Form(..., description='Enter approximate altitude integer value without any decimal points'), 
                         select_input_data_source_option: SoilTempDataSources = Form(..., description="Select data source option"),
                         input_data: str = Form(..., description='Enter folder path to the input data format'), 
                         targets_string: str = Form(..., description='Enter comma seperated target names(names should match trained model target names. Example: ST2,ST5,ST10,ST20,ST50,ST100)'), 
                         models_folder_path:str = Form(..., description='Enter trained models folder path')):
    try:
        predictions = {}
        predictions_series = {}
        predictions_df ={}
        # Folder where models are located
        model_folder = models_folder_path        
        targets = targets_string.split(',')
        # Define the test inputs folder path
        test_inputs_folder_path = input_data
        # Assuming target_variables is a list of target variable names like ST2, ST5, ST10....
        sorted_target_variables = sorted(targets, key=lambda x: int(re.search(r'\d+', x).group()))# Sort them by their numeric extension ST2, ST5...
        
        models = {}
        # Load models
        for target in sorted_target_variables:
            model_path = os.path.join(model_folder, f"{target}.joblib")
            models[target] = load(filename=f"{model_path}")        

        # Initialize test_input_df with the data from the first input file
        first_target = sorted_target_variables[0]
        if(select_input_data_source_option and select_input_data_source_option.lower() == 'file'):
            first_file_path = os.path.join(test_inputs_folder_path, f"{first_target}_X_test.xlsx")
            if os.path.isfile(first_file_path):
                input_df = pd.read_excel(first_file_path, index_col='time')
            else:
                first_file_path = os.path.join(test_inputs_folder_path, f"{first_target}_X_test.csv")
                if os.path.isfile(first_file_path):
                    input_df = pd.read_csv(first_file_path, index_col='time')
                else:
                    raise FileNotFoundError(f"Input data file not found for target: {first_target}")

            test_input_df = input_df.copy()
        else:
            test_input_df = await fetch_meteorology_data_from_MET_No_frost(latitude, longitude, altitude)    
        for target in sorted_target_variables:
            model = models[target]
            # Filter columns based on the input data file for the current target
            target_file_path = os.path.join(test_inputs_folder_path, f"{target}_X_test.xlsx")
            if os.path.isfile(target_file_path):
                target_input_columns = pd.read_excel(target_file_path, index_col='time')
            else:
                target_file_path = os.path.join(test_inputs_folder_path, f"{target}_X_test.csv")
                if os.path.isfile(target_file_path):
                    target_input_columns = pd.read_csv(target_file_path, index_col='time')
                else:
                    raise FileNotFoundError(f"Input data file not found for target: {target}")
            # Filter test_input_df columns to match those of the current target
            target_columns = target_input_columns.columns
            input_data = test_input_df[target_columns]
            input_data.index = test_input_df.index   
            # Perform prediction
            predictions[target] = model.predict(input_data)
            predictions_series = pd.Series(predictions[target])
            predictions_series.name = target
            predictions_df = predictions_series.to_frame()
            predictions_df.index = test_input_df.index
            # Concatenate with input data
            test_input_df = pd.concat([test_input_df, predictions_df], axis=1)
        predicted_data = test_input_df.copy()
        # Get the current date
        current_date = datetime.now()
        # Format the date with dashes
        formatted_date = current_date.strftime("%Y-%m-%d")
        predicted_data.to_excel(os.path.join(test_inputs_folder_path, f"{formatted_date}_soil_predictions.xlsx"))
        return {"predicted_data": predicted_data.to_dict(orient="records")}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

