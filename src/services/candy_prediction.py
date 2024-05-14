# %%
import numpy as np
from scipy.signal import find_peaks
import sympy as sym
from sympy import solve
from pydantic import BaseModel, Field
from typing import Dict, List, Any
import http


class candy_prediction_response(BaseModel):
    results: List[Dict[str, Any]]
class candy_request(BaseModel):
    dataHighCal: Dict[str, List[float]] # {'x' : [], 'y': []} 
    dataLowCal: Dict[str, List[float]] # {'x' : [], 'y': []} 
    dataCVSample: Dict[str, List[float]] # {'x' : [], 'y': []} 
    dataCASample: Dict[str, List[float]] # {'x' : [], 'y': []} 
    highConc: float = 50
    lowConc: float = 12.5
# %%
class Halls():
    def __init__(self, req: candy_request):

        '''
        assuming all the data from Djuli are equal: {'x':[], 'y':[]}
        '''
        self.__dataHighCal = req.dataHighCal
        self.__dataLowCal = req.dataLowCal
        self.__dataCVSample = req.dataCVSample
        self.__dataCASample = req.dataCASample
        self.__highConc = req.highConc
        self.__lowConc = req.lowConc
        # print (len(self.__dataHighCal['x']), len(self.__dataLowCal['x']), len(self.__dataCVSample['x']),len(self.__dataCASample['x']))
        pass

    def validate(self):
        if (len(self.__dataHighCal['x']) < 604) or (len(self.__dataHighCal) == 0): # reminder: check if the data is full length - lx to check the full length
            return False, "Invalid calibraion file. Please provide a valid calibraion file"
        if (len(self.__dataLowCal['x']) < 604) or (len(self.__dataLowCal) == 0):
            return False, "Invalid calibraion file. Please provide a valid calibraion file"
        if (len(self.__dataCVSample['x']) <604) or (len(self.__dataCVSample) == 0):
            return False, "Invalid data file. Please provide a valid data file"
        if (len(self.__dataCASample['x']) < 2000) or (len(self.__dataCASample) == 0):
            return False, "Invalid data file. Please provide a valid data file"
        return True, ""

    def __IfromData(self, data):
        index_2ndScan = 604
        E = np.asarray(data['x'])[index_2ndScan:]
        I = np.asarray(data['y'])[index_2ndScan:]
        index_all = np.flatnonzero(E < -0.1)                       #Finds values less than -0.1V
        index_point1 = np.min(index_all)                           #Creates bounds for area of interest 
        index_point2 = np.max(index_all)                          #Creates bounds for area of interest
        index_point3 = index_point1 + index_point2
        I_max = np.max((I[index_point2:index_point3])-(I[0:index_point1]))      #a-b != b-a
        return I_max

    def __checkDominated(self): 
        '''
        check the dominated ingredients;
        
        '''
        index_2ndScan = 604
        E_2ndCV = np.asarray(self.__dataCVSample['x'])[index_2ndScan:]
        I_2ndCV = np.asarray(self.__dataCVSample['y'])[index_2ndScan:]
        peaks, _ = find_peaks(I_2ndCV)
        E_peaks = E_2ndCV[peaks]
        min_E_peaks = min([E for E in E_peaks if E > 0.7])
        area = np.trapz(E_2ndCV, I_2ndCV)
        
        Vend_index = max(np.flatnonzero(E_2ndCV >= 0.5))
        Vstart_index = min(np.flatnonzero(E_2ndCV >= 0.5))

        E_region = E_2ndCV[Vstart_index:Vend_index]
        I_region = I_2ndCV[Vstart_index:Vend_index]

        parameter = np.polyfit(E_region,I_region,3)[0]

        if (min_E_peaks > 0.75) and (min_E_peaks < 0.85):
            dominated = 'cherry'
        elif (parameter < 20) and (area > -0.5):
            dominated = 'Bare candy'
        elif parameter > 20:
            dominated = 'Menthol'
        elif (parameter < 20) and (area < -0.5):
            dominated = 'Eucalyptol'
        return dominated

    def __parameterCalibraiton(self):
        I_High = self.__IfromData(self.__dataHighCal)    
        I_Low = self.__IfromData(self.__dataLowCal)     
        I_list = np.array([I_High,I_Low])
        c_list = np.array([self.__highConc, self.__lowConc])
        parameters = np.polyfit(c_list, I_list, 1)
        return {'C0': parameters[0], 'C1': parameters[1]}
    def __resolveCV(self):
        I_sampleCV = self.__IfromData(self.__dataCVSample)
        parameters = self.__parameterCalibraiton()
        C0 = parameters['C0']
        C1 = parameters['C1']
        x = sym.Symbol('x')
        eqn = C0*x + C1 - I_sampleCV
        try:
            result_dominated = float(solve(eqn, x)[0])
            return result_dominated
        except:
            result_dominated = 0
            return result_dominated
    def __totalConc(self):
        try:
            I_ca = np.asarray(self.__dataCASample['y'])[800:]
            peaks, _ = find_peaks(I_ca, height=0.2)
            I_max = np.max(I_ca[peaks])
            base_index = np.flatnonzero(I_ca == I_max) - 5
            I_base = I_ca[base_index]
            I_CAdiff = abs(I_max-I_base)
        except:
            I_CAdiff = np.zeros(1)
        return I_CAdiff
    def resultFinal(self):
        dominated_result = self.__resolveCV()
        I_CAdiff = self.__totalConc()
        dominated_comp = self.__checkDominated()
        nonDominated_comp = 'Eucalyptol'
        
        result_altern = dominated_result/100 * I_CAdiff

        nonDominated_result = np.zeros(1)
        if dominated_comp == 'Menthol':
            nonDominated_result += result_altern/8.2
            nonDominated_comp ='Eucalyptol'
        elif dominated_comp == 'Eucalyptol':
            nonDominated_result += result_altern/3.2
            nonDominated_comp = 'Menthol'
        elif dominated_comp == 'cherry':
            nonDominated_result += result_altern/3
            dominated_comp = 'Menthol'
        if nonDominated_result < 0.05:
            nonDominated_result = np.zeros(1)
            result_altern = result_altern/4
        nonDominated_result_ = nonDominated_result[0]
        result_altern = result_altern[0]- nonDominated_result_
        result_altern_ = result_altern*0.4426
        result_list = [{'analyte': dominated_comp, 'value': round(result_altern_,4), 'unit': '%'}, {'analyte': nonDominated_comp, 'value': round(nonDominated_result_,4), 'unit': '%'}]
        return candy_prediction_response(results = result_list)
            








        

    

        



    
# %%
