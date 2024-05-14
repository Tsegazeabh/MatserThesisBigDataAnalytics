# %%
import numpy as np
from pydantic import BaseModel, Field
from typing import List

class standard_addition_response(BaseModel):
    st_add: float = Field(..., description="predicted value")

class standard_addition_request(BaseModel):
    Cstd: float = Field(..., description="stock standard concentration")
    vflask: float = Field(..., description="final volume (fixed at each experiment)")
    vunk:float = Field(..., description="volume of unknown sample")
    vadd: List[float] = Field(..., description="added volume")
    mean: List[float] = Field(..., description="response from Djuli plots - can be chronoamp or potentiometric or voltammetric")

class Standard_addition:
    '''
    This method takes: 
    1. fixed volume of known samples, 
    2. fixed standard addition solution concentration, 
    3. fixed final volume
    4. variable standard addition volume but needs to be smaller than the final volume
    This method gives a concentration to the unknown concentration 
    For example, 
    1. Prepare 3 beakers
    2. prepare 10mM of standard addition solution
    3. in each test, add 10mL of unknown sample
    4.1 beaker 1: 10mL of standard addition solution
    4.2 beaker 2: 15mL of standard addition solution
    4.3 beaker 3: 20mL of standard addition solution
    5 top up all beakers to 50mL of PBS to the final solution. 
    6 record the response using chronoamp or potentiometric or voltammetric
    7 the script gives output of the concentration to the unknown concentration 

    '''
    def __init__(self, req: standard_addition_request):
        self.__Cstd = req.Cstd          # stock standard concentration
        self.__vflask = req.vflask      # final volume (fixed at each experiment)
        self.__vunk = req.vunk          # volume of unknown sample
        self.__vadd = req.vadd          # added volume
        self.__response = req.mean      # response from Djuli plots - can be chronoamp or potentiometric or voltammetric

    def validate(self):
        if np.isnan(self.__Cstd) or self.__Cstd < 0:
            return False, "Invalid Csrd. Please provide a valid standard concentration"
        if np.isnan(self.__vflask) or self.__vflask < 0:
            return False, "Invalid vflask. Please provide a valid final volume"
        if np.isnan(self.__vunk) or self.__vunk < 0:
            return False, "Invalid vunk. Please provide a valid volume of unknown sample"
        if len(self.__vadd) == 0:
            return False, "Empty vadd. Please provide a valid added volume"
        if len(self.__vadd) != len(self.__response):
            return False, "Length of vadd and response must match"
        return True, ""

    def __CalCstd(self):
        Csa = [self.__Cstd * v / self.__vflask for v in self.__vadd] # calculation of the standard addition concentration
        return Csa

    def analysisMethod(self):
        Csa = self.__CalCstd()
        slope, intercept = np.polyfit(Csa, self.__response, 1)
        X0 = (0 - intercept)/slope # X intercept
        Cunk = -X0 * self.__vflask/ self.__vunk
        return standard_addition_response(st_add=Cunk)
# %%
