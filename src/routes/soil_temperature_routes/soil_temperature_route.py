from datetime import datetime
import os
import re
from exceptiongroup import catch
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
        print("reached 0")
        predictions = {}
        predictions_series = {}
        predictions_df ={}
        # Folder where models are located
        model_folder = models_folder_path
        print('Model:', model_folder)        
        targets = targets_string.split(',')
        print('Targets:', targets)
        # Define the test inputs folder path
        test_inputs_folder_path = input_data
        print('Folder Path:', test_inputs_folder_path)
        # Assuming target_variables is a list of target variable names like ST2, ST5, ST10....
        sorted_target_variables = sorted(targets, key=lambda x: int(re.search(r'\d+', x).group()))# Sort them by their numeric extension ST2, ST5...
        print('Tagets: ', sorted_target_variables)
        models = {}
        # Load models
        for target in sorted_target_variables:
            model_path = os.path.join(model_folder, f"{target}.joblib")
            print("reached 1: ", model_path, target)
            models[target] = load(filename=f"{model_path}") 
            print("after load model")   
        
        print('Reached after load')        

        # Initialize test_input_df with the data from the first input file
        first_target = sorted_target_variables[0]
        if(select_input_data_source_option and select_input_data_source_option.lower() == 'file'):
            first_file_path = os.path.join(test_inputs_folder_path, f"{first_target}_X_test.xlsx")
            print('Reached after file path', first_file_path)
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

        print('Test Input DF:', test_input_df)    
        for target in sorted_target_variables:
            print("reached 2")
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
            print('Reached after target input df: ', target_input_columns)
            # Filter test_input_df columns to match those of the current target
            target_columns = target_input_columns.columns
            print('test columns: ', target_columns)
            input_data = test_input_df[target_columns]
            print('input data: ', input_data)
            input_data.index = test_input_df.index   
            # Perform prediction
            print('target_columns: ', input_data)
            predictions[target] = model.predict(input_data)
            print('After prediction: ', predictions[target])
            # Changes the predicted array values to pandas series
            predictions_series = pd.Series(predictions[target])
            predictions_series.name = target
            print('Predictions series: ', predictions_series)
            # Convert the Series to a DataFrame
            predictions_df = predictions_series.to_frame()
            # Set index
            predictions_df.index = test_input_df.index
            print('Predicteds DF: ', predictions_df)
            # Concatenate with input data
            test_input_df = pd.concat([test_input_df, predictions_df], axis=1)
            print('After Test conc: ', test_input_df.columns)

        print("reached 3")
        predicted_data = test_input_df.copy()
        print("After result df: ", predicted_data.columns)
        # Get the current date
        current_date = datetime.now()
        # Format the date with dashes
        formatted_date = current_date.strftime("%Y-%m-%d")
        predicted_data.to_excel(os.path.join(test_inputs_folder_path, f"{formatted_date}_soil_predictions.xlsx"))
        return {"predicted_data": predicted_data.to_dict(orient="records")}
    
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))

