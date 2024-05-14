from os import environ
from typing import List, Any, Dict
from fastapi import FastAPI, UploadFile, Response, status, Body
from fastapi.responses import RedirectResponse
import uvicorn

import common.constants as constants
import services.draw_circuit as service_draw_circuit
import services.dt6_manager as service_dt6manager
import services.ImageAnalysis.image_recognition as service_image_recognition
from services.standard_addition import standard_addition_response, standard_addition_request, Standard_addition as service_standard_addition
from models.vue_front_end import PlotResponse
from services.candy_prediction import candy_prediction_response, candy_request, Halls as service_candy_prediction
from services.GOx_abcam import abcam_response, abcam_request, Abcam as service_GOx_Abcam
from services.infecto import infecto_response, infecto_request, InfectoTest as service_Infecto
from utils.firebase_storage import firebase_admin
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from routes.agrisenze_routes.agrisenze_data_route import agrisenzeData
from routes.crop_routes.crop_data_route import cropData
from routes.farming_practice_routes.farming_practice_data_route import farmingPracticeData
from routes.geographic_data_route import geographicData
from routes.IoT_sensors_routes.IoT_sensors_data_route import IoT_sensors_Data
from routes.soil_routes.soil_data_route import soilData
from routes.topography_routes.topography_data_route import topographyData
from routes.weather_routes.weather_data_route import weatherData
from routes.big_agri_data_route import agriBigData
from routes.agri_big_dataset.agri_big_dataset_route import agriBigDataset
from routes.soil_temperature_routes.soil_temperature_route import predictTarget



app = FastAPI(
    title="Djuli Python API",
    description="This Python API contains part of the djuli back-end.",
    version=constants.VERSION,
)
# Custom metadata for the OpenAPI schema
custom_openapi_metadata = {
    "info": {
        "title": "AgriSenze Big Data Analytics API Documentation",
        "description": "This is a custom description for AgriSenze API",
        "version": "1.0.0"
    },
    "servers": [
        {"url": "http://localhost:8002", "description": "Local Development Server"},
        {"url": "https://api.agrisense.zimmerpeacock.com", "description": "Production Server"}
    ],
    # Add more custom metadata as needed
}

# Function to override the default OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Djuli Python API",
        version=constants.VERSION,
        description="This Python API contains part of the djuli backend.",
        routes = app.routes
    )

    # Merge custom metadata with generated schema
    openapi_schema["info"] = custom_openapi_metadata["info"]
    openapi_schema["servers"] = custom_openapi_metadata["servers"]
    # Add more customizations here as needed

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Assign the custom_openapi function to app.openapi
app.openapi = custom_openapi

#===========================================
# API End Points
#===========================================
# Allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with the origin of your frontend application
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

#======================================
# Agrisenze Big Data Analytics Services included below
#======================================
# Agrisenze Big Data APIs
app.include_router(agriBigDataset)
app.include_router(predictTarget)
app.include_router(agrisenzeData)
app.include_router(cropData)
app.include_router(farmingPracticeData)
app.include_router(geographicData)
app.include_router(IoT_sensors_Data)
app.include_router(soilData)
app.include_router(topographyData)
app.include_router(weatherData)
app.include_router(agriBigData)
#=============================================== ZP Python endpoints =================
@app.get(constants.ROOT_URL + "/drawCircuit/{circuit}",
         name="Draw Circuit", summary="Returns an image on base64 representing the given circuit formatted as standard djuli response",
         tags=["Impedance Fit"], response_model = PlotResponse)
async def draw_circuit_req(circuit: str):
    return service_draw_circuit.draw_circuit_req(circuit)

@app.get(constants.ROOT_URL + "/drawCircuitRaw/{circuit}",
         name="Draw Circuit Raw", summary="Returns an image on base64 representing the given circuit",
         tags=["Impedance Fit"])
async def draw_circuit_req(circuit: str):
    return service_draw_circuit.draw_circuit_raw_req(circuit)


@app.post(constants.ROOT_URL + "/openDT6", status_code=200,
         name="Open DT6 File", summary="Returns extracted data of the DT6 on the standard data storage on djuli",
         tags=["Data Extraction"], response_model = PlotResponse)
async def open_dt6(file: UploadFile, response: Response):
    return await service_dt6manager.openFile(file, response)


@app.post(constants.ROOT_URL + "/imageRecognition", status_code=200,
         name="Cookie Image Recognition", summary="Returns a string stating whether a cookie is burned or not on standard djuli front-end response",
         tags=["Image Recognition"])
async def imageRecognition(data:List[Any], response: Response):
    return service_image_recognition.predict_from_request(data, response)


@app.post(constants.ROOT_URL + "/imageRecognitionFromBit64", status_code=200,
         name="Cookie Image Recognition Raw", summary="Returns a string stating whether a cookie is burned or not on raw format",
         tags=["Image Recognition"])
async def imageRecognition(data:Dict[str,Any], response: Response):
    return service_image_recognition.predict_from_bit64_request(data["data"], response)

@app.post(constants.ROOT_URL + "/standardAddition", status_code=200,
         name="Standard Addition", summary="Returns the value of unknown volume",
         tags=["Data Extraction"], response_model = standard_addition_response)
async def standardAddition(response: Response, standard_add_req: standard_addition_request):
    standard_add = service_standard_addition(standard_add_req)
    valid, message = standard_add.validate()
    if not valid:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return message
    return standard_add.analysisMethod()


@app.post(constants.ROOT_URL + "/candyPrediction", status_code=200,
         name="candy ingredient prediction", summary="Returns the value of Menthol and Eucalyptol concentration",
         tags=["Prediction Model"], response_model = candy_prediction_response) 
async def candyPrediction(response: Response, candy_pred_req: candy_request):
    candy_pred = service_candy_prediction(candy_pred_req)
    valid, message = candy_pred.validate()
    if not valid:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return message
    return candy_pred.resultFinal()

@app.post(constants.ROOT_URL + "/GOxAbcam", status_code=200,
         name="colorimetric GOx assay", summary="Returns the value of GOx concentration in mU/mL, U/g and LoD check",
         tags=["Data Extraction"], response_model = abcam_response) 
async def candyPrediction(response: Response, GOx_req: abcam_request):
    abcam = service_GOx_Abcam(GOx_req)
    valid, message = abcam.validate()
    if not valid:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return message
    return abcam.Results()

@app.post(constants.ROOT_URL + "/InfectoTest", status_code=200,
         name="infestoTest GmbH", summary="Returns the concentration of GmbH in mM",
         tags=["Data Extraction"], response_model = infecto_response) 
async def candyPrediction(response: Response, infecto_req: infecto_request):
    infecto = service_Infecto(infecto_req)
    valid, message = infecto.validate()
    if not valid:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return message
    return infecto.analysis()



# Run server
server_port = environ.get('PORT') if environ.get('PORT') else constants.SERVER_PORT
server_host = environ.get('HOST') if environ.get('HOST') else constants.SERVER_HOST
if __name__ == '__main__':
    uvicorn.run(app, port=server_port, host=server_host)
