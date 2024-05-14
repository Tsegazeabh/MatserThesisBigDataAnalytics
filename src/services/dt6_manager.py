import os
import re
import numpy as np
from os import path
from random import randint
from shutil import rmtree
from datetime import datetime
from fastapi import status
from models.vue_front_end import PlotResponse


async def openFile(uploaded_file, response):
  uniqueId = randint(1, 10000000000)
  tempFolder = f"{os.getcwd()}/src/service/dt6Exec/tempFolder{uniqueId}"
  warnings = []
  try:
    fileName = uploaded_file.filename
    os.makedirs(tempFolder)
    buffer = await uploaded_file.read()
    # Define the variables
    tempFileOutput=f"{tempFolder}/tempOut{uniqueId}.txt"
    tempFileInput=f"{tempFolder}/{fileName}"
    # Save the temporarily file
    with open(tempFileInput, "wb+") as binary_file:
      binary_file.write(buffer)

    commandTranslator = f"wine {os.getcwd()}/src/service/dt6Exec/DLL/DL4CmdLine.exe '{tempFileInput}' /EXDT6 /F{tempFileOutput}"
    os.system(commandTranslator)
    if not path.isfile(tempFileOutput):
      raise ValueError('Error while trying to process your file. Please verify it contains valid information')

    #Read the lines and erase all the files
    with open(tempFileOutput) as f:
      linesTempF = [line.strip() for line in f.readlines()]
    rmtree(tempFolder)

    initialDate = None
    headers_table = [header for header in linesTempF[0].split("\t") if header]
    units_table = [unit for unit in linesTempF[1].split("\t") if unit]
    # Verify if the coument is multivariable and then select the values should be extracted
    multivariable = len(headers_table) > 1
    if multivariable:
      # We add one because it is necesary to consider the first time column
      index_multivariable = [i + 1 for i, item in enumerate(headers_table) if re.search(r"(Voltage)|(Current)", item)]

      # Filter the units by valid elements
      index_units_table = [i for i, item in enumerate(units_table) if re.search(r"(^[GMkmunf]?V$)|(^[GMkmunf]?A$)", item)]
      if len(index_units_table):
        # Extands the current index by filtering with the units.
        extended_index_mult = [i for i, item in enumerate(headers_table) if re.search(r"(CH[\d]+)|(SM[\d]+)", item)]
        index_multivariable.extend([indx +1 for indx in list(set(extended_index_mult) & set(index_units_table))])
        if len(index_multivariable) == 0:
          index_units_table.sort()
          index_multivariable.extend([indx +1 for indx in index_units_table])
    else:
      index_multivariable = [1]  # Because it does not have the datestamp header

    X = []
    Y = []
    # Iterate over the values
    for line in linesTempF[2:]:
      splitLine = line.split("\t")
      if not splitLine:
        continue
      if not multivariable:
        splitLine = [x for x in splitLine if x]
      date = get_date_from_string(splitLine[0])
      # If it is multivariable then executes a different path.
      if multivariable:
        # Verifies the line has correct size
        if any(indx > len(splitLine) for indx in index_multivariable):
          warnings.append("The element in line '$(line)' does not have a valid data")
          continue
        formatted_value = []
        for index in index_multivariable:
          try:
            numeric_value = float(splitLine[index])
          except:
            numeric_value = np.nan
          formatted_value.append(numeric_value)
        valid_numerical_value = len(formatted_value) > 0
      else:
        try:
          formatted_value = [float(splitLine[-1])]
          valid_numerical_value = True
        except ValueError:
          formatted_value = [np.nan]
          valid_numerical_value = False
      if date is None and not valid_numerical_value:
        continue
      if (date is None) != (not valid_numerical_value):  # It means one of this is valid but the other no
        warnings.append("The element '$(line)' does not have a valid data")
        continue
      if initialDate is None:
        initialDate=date
      time_diff_sec = (date-initialDate).total_seconds()
      # The addition in the array is dynamic because the data could have faulty lines
      X.append(time_diff_sec)
      # Y value is always an array of arrays
      Y.append(formatted_value)
    if not len(Y):
      raise ValueError("The file doesn't contain electrochemical information. Please contact the administrator of the system.")

    Y = np.transpose(np.array(Y))
    X_np = np.array(X)
    data = []
    headers_table_filt = [ headers_table[indx_header-1] for indx_header in index_multivariable ]
    for j in range(len(Y[:,0])):
      if np.all(np.isnan(Y[j,:])):
        continue
      header = ""
      if j < len(headers_table_filt):
        header = headers_table_filt[j]
      data.append({
        "X":X_np[~np.isnan(Y[j,:])].tolist(),
        "Y":Y[j,:][~np.isnan(Y[j,:])].tolist(),
        "date":int(initialDate.timestamp() * 1000),
        "title":header
      })
    return PlotResponse.get_data_response("openDT6", {"extracted_data": data}, warnings)

  except Exception as e:
    last_error = f"Problem in the server please contact the administrator. Error: {str(e)}"
    response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    return PlotResponse.get_error_response("openDT6", warnings, last_error)

  finally:
    if path.isdir(tempFolder):
      rmtree(tempFolder)


def get_date_from_string(stringdate):
  mmddYYYY_hhmmss=r"^([0-1]?[0-9])[\/-]([0-3]?[0-9])[\/-]([0-9]{4})[ ]([0-2]?[0-9])[:]([0-5]?[0-9])[:]([0-5]?[0-9])[ ]?(AM|PM)?"
  rMatch=re.match(mmddYYYY_hhmmss,stringdate)
  if rMatch and int(rMatch.group(1)) <=12:
    hour=int(rMatch.group(4))
    if hour == 12:
      if rMatch.group(7) == "AM":
        hour = 0
    elif rMatch.group(7) =="PM":
      hour+=12
    return datetime(int(rMatch.group(3)),int(rMatch.group(1)),int(rMatch.group(2)),hour,int(rMatch.group(5)),int(rMatch.group(6)))
  ddmmYYYY_hhmmss=r"^([0-3]?[0-9])[\/-]([0-1]?[0-9])[\/-]([0-9]{4})[ ]([0-2]?[0-9])[:]([0-5]?[0-9])[:]([0-5]?[0-9])[ ]?(AM|PM)?"
  rMatch=re.match(ddmmYYYY_hhmmss,stringdate)
  if rMatch and int(rMatch.group(2)) <=12:
    hour=int(rMatch.group(4))
    if hour == 12:
      if rMatch.group(7)=="AM":
        hour = 0
    elif rMatch.group(7)=="PM":
      hour+=12
    return datetime(int(rMatch.group(3)),int(rMatch.group(2)),int(rMatch.group(1)),hour,int(rMatch.group(5)),int(rMatch.group(6)))
  YYYYmmdd_hhmmss=r"^([0-9]{4})[\/-]([0-1]?[0-9])[\/-]([0-3]?[0-9])[ ]([0-2]?[0-9])[:]([0-5]?[0-9])[:]([0-5]?[0-9])[ ]?(AM|PM)?"
  rMatch=re.match(YYYYmmdd_hhmmss,stringdate)
  if rMatch and int(rMatch.group(2)) <=12:
    hour=int(rMatch.group(4))
    if hour == 12:
      if rMatch.group(7)=="AM":
        hour = 0
    elif rMatch.group(7)=="PM":
      hour+=12
    return datetime(int(rMatch.group(1)),int(rMatch.group(2)),int(rMatch.group(3)),hour,int(rMatch.group(5)),int(rMatch.group(6)))
  YYYYddmm_hhmmss=r"^([0-9]{4})[\/-]([0-3]?[0-9])[\/-]([0-1]?[0-9])[ ]([0-2]?[0-9])[:]([0-5]?[0-9])[:]([0-5]?[0-9])[ ]?(AM|PM)?"
  rMatch=re.match(YYYYddmm_hhmmss,stringdate)
  if rMatch and int(rMatch.group(3)) <=12:
    hour=int(rMatch.group(4))
    if hour == 12:
      if rMatch.group(7)=="AM":
        hour = 0
    elif rMatch.group(7)=="PM":
      hour+=12
    return datetime(int(rMatch.group(1)),int(rMatch.group(3)),int(rMatch.group(2)),hour,int(rMatch.group(5)),int(rMatch.group(6)))
  return None
