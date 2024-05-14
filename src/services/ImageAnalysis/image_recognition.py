import os
from os import path
import re
from . import prediction_script as cookies_modules
from base64 import urlsafe_b64decode
from random import randint
from fastapi import status
from models import vue_front_end


regexGetTypeData = r"^data:image/([a-zA-Z]+);base64,(.*)$"


def predict(fileRoute):
  return cookies_modules.predict(fileRoute)


def predict_from_bit64(dataBit64):
  # Decode the image file from bit64
  rMatch = re.match(regexGetTypeData, dataBit64)
  if not rMatch:
    return None
  typeFile = rMatch.group(1)
  uniqueId = randint(1, 10000000000)
  tempFile = f"{os.getcwd()}/src/service/ImageAnalysis/tempOut{uniqueId}.{typeFile}"
  try:
    output = urlsafe_b64decode(rMatch.group(2).encode('ascii'))
    with open(tempFile, "wb") as binary_file:
      binary_file.write(output)
    return cookies_modules.predict(tempFile)
  except Exception as err:
    print(err)
    return None
  finally:
    if path.isfile(tempFile):
      os.remove(tempFile)


def predict_from_bit64_request(dataBit64, response):
  prediction = None
  try:
    prediction = predict_from_bit64(dataBit64)
  except Exception as e:
    response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    return {"error": f"Error while processing the image. Message: {str(e)}"}
  if prediction:
    data = {"prediction": prediction}
  else:
    response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    data = {"error": "Not possible to predict"}
  return {"data": data, "warnings":[] }


def predict_from_request(data, response):
  warnings = []
  dataTable = []
  try:
    for elem_analyze in data:
      prediction = predict_from_bit64(elem_analyze["extractedData"])
      fileName = elem_analyze["name"]
      if prediction is None:
        warnings.append(f"The file {fileName} was not possible to process")
        continue
      dataTable.append({
        "Name": fileName,
        "Prediction": prediction
      })
    predictionTable = vue_front_end.Table(
      "TABLE_PREDICTION", "Image Recognition", dataTable, ["Name", "Prediction"]
    )
    tables = [predictionTable]
    return vue_front_end.formatCards(
      "Vue Complex Analysis",
      tables,
      warnings
    )
  except Exception as e:
    lastError = str(e)
    response.status_code = status.HTTP_400_BAD_REQUEST
    return vue_front_end.get_error_response("Image Recognition",lastError, warnings)
