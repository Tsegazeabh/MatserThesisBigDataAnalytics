# this algorithm is used for determing infestoTest GmbH
# %%
import numpy as np
from pydantic import BaseModel
from typing import List, Dict, Any
# %%

class infecto_response(BaseModel):
    results: List[Dict[str,Any]]

class infecto_request(BaseModel):
    unit: str = 'uA'
    slope: float = 4.37e-8 # Amp per mM
    intercept: float = 8.96e-10 # Amp
    baseFile: Dict[str,List[float]]
    sampleFile: Dict[str,List[float]]


class InfectoTest():
    def __init__(self, req: infecto_request) -> None:
        self.__unit = req.unit
        self.__slope = req.slope
        self.__intercept = req.intercept
        self.__baseFile = req.baseFile
        self.__sampleFile = req.sampleFile

    def validate(self):
        if len(self.__baseFile['x']) == 0:
            return False, "Invalid file. Please provide a valid file"
        if len(self.__sampleFile['x']) == 0:
            return False, "Invalid file. Please provide a valid file"
        return True, ""

    def analysis(self):
        if self.__unit == 'A':
            multiplier = 1
        elif self.__unit == 'uA':
            multiplier = 1e-6
        elif self.__unit == 'nA':
            multiplier = 1e-9
        result_list = []
        x = np.array(self.__sampleFile['x']) # converting x into np.array
        y_sample = np.array(self.__sampleFile['y']) * multiplier # converting y into np.array
        y_base = np.array(self.__baseFile['y']) * multiplier
        y_diff = y_sample - y_base
        startIndex_ = np.where(x >= 450)[0][0] # identify the index starting from time 450 s
        meanCurrent = y_diff[startIndex_:].mean()
        
        result = (meanCurrent - self.__intercept)/self.__slope #intercept is in A, slope is in A/10uM
        result_list = [{'analyte': 'D-Lactate', 'value': round(result * 10,2), 'unit': 'mM'}]
        return infecto_response(results = result_list)


# %%
