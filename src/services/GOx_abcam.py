import numpy as np
from scipy import stats
from pydantic import BaseModel
from typing import Dict, List, Any

class abcam_response(BaseModel):
    GOx_result: Dict[str, Dict[str, Any]]

class abcam_request(BaseModel):
    plateLayout: Dict[str,str]
    absorbanceReading: Dict[str, Dict[str,float]] # {'x' : [], 'y': []} 
    timeReading: Dict[str, Dict[str,float]] # {'x' : [], 'y': []} 
    stockVolume: float = 0.5
    stockGram: float = 5
    dilutionID: List[str]
    dilutionFactor: List[int]
    bottleActivity: float


class Abcam():
    def __init__(self, req: abcam_request):
        self.__plateLayout = req.plateLayout # the plate format ie where the standard and samples are located
        self.__absorbanceReading = req.absorbanceReading # the absorbance reading from the reader
        self.__timeReading = req.timeReading # the time reading from the reader
        self.__stockVolume = req.stockVolume # the volume added into each well
        self.__stockGram = req.stockGram # the weight of GOx added into the dilution
        self.__dilutionID = req.dilutionID # the ID for the dilution written in D1, D2 etc
        self.__dilutionFactor = req.dilutionFactor # the dilution factors corresponding to the ID
        self.__bottleActivity = req.bottleActivity # the bottle activities

    def validate(self):
        if len(self.__plateLayout) == 0: # reminder: check if the data is full length - lx to check the full length
            return False, "No plate uploaded"
        if (len(self.__absorbanceReading) == 0):
            return False, "No reading uploaded"
        return True, ""
    def __well_from_ID(self, value_, dict_): 
        '''
        identify the well number from the descritption
        for example: to identify the well corresponding to 'Standard # 8' is well H1 and H2 
        return a list
        for example:
        input: value_ = 'Standard # 8', dict_: {'A1': 'Standard # 1',
                                                'A2': 'Standard # 1',
                                                'A3': 'S1 D1',
                                                'A4': 'S1 D1',
                                                'A5': 'S1 D1',
                                                'B1': 'Standard # 2',
                                                'B2': 'Standard # 2',
                                                'B3': 'S1 D2',
                                                'B4': 'S1 D2',
                                                'B5': 'S1 D2',
                                                'C1': 'Standard # 3',
                                                'C2': 'Standard # 3',
                                                'D1': 'Standard # 4',
                                                'D2': 'Standard # 4',
                                                'E1': 'Standard # 5',
                                                'E2': 'Standard # 5',
                                                'F1': 'Standard # 6',
                                                'F2': 'Standard # 6',
                                                'G1': 'Standard # 7',
                                                'G2': 'Standard # 7',
                                                'H1': 'Standard # 8',
                                                'H2': 'Standard # 8'}
        return: ['H1', 'H2']
        '''
        wells = []
        for key, value in dict_.items():
            if ((type(value) != np.float64)):
                if (value_ in value):
                    wells.append(key)
        return wells
    def __dilutionMapping(self):
        '''
        mapping the dilution corresponding to each well
        return a dictionary as {well_ID: dilution factor}
        example:
        {'A1': 1,
        'A2': 1,
        'A3': 250000,
        'A4': 250000,
        'A5': 250000,
        'B1': 1,
        'B2': 1,
        'B3': 500000,
        'B4': 500000,
        'B5': 500000,
        'C1': 1,
        'C2': 1,
        'D1': 1,
        'D2': 1,
        'E1': 1,
        'E2': 1,
        'F1': 1,
        'F2': 1,
        'G1': 1,
        'G2': 1,
        'H1': 1,
        'H2': 1}
        '''
        dilution_dict = dict(zip(self.__dilutionID, self.__dilutionFactor))
        self.__dilution_map = {}
        for id in self.__plateLayout.values():
            if ((type(id) != np.float64)):
                if id.split(' ')[-1] in dilution_dict.keys():
                    wells = self.__well_from_ID(id, self.__plateLayout)
                    for well in wells:
                        self.__dilution_map[well] = dilution_dict[id.split(' ')[-1]]
                elif id.split(' ')[-1] not in dilution_dict.keys():
                    wells = self.__well_from_ID(id, self.__plateLayout)
                    for well in wells:
                        self.__dilution_map[well] = 1
        return self.__dilution_map

    def __onlyReadWell(self, raw_dict, wells):
        '''
        function that only read the non-empty wells
        raw_dict are the dictionary contains all wells, in a form of dictionary
        wells are the non empty wells, in a form of a list
        returns a dictionary
        '''
        selectedDict = {id_:raw_dict[id_] for id_ in  wells}
        return selectedDict
    def __standardWells(self):
        '''
        {well_description: concentration} for all the standards. 
        It is standarised - should be a template.
        example:
        {'Standard # 1': 10.0,
        'Standard # 2': 5.0,
        'Standard # 3': 2.5,
        'Standard # 4': 1.25,
        'Standard # 5': 0.625,
        'Standard # 6': 0.3125,
        'Standard # 7': 0.15625,
        'Standard # 8': 0}
        This also give the list of sample wells and standard wells
        '''
        self.__standard_IDs = [f'Standard # {y}' for y in range(1,9)]
        self.__standard_conc = [10/(2**n) for n in range(0,7)]
        self.__standard_conc.append(0)
        self.__standard_dict = dict(zip(self.__standard_IDs, self.__standard_conc))
        self.__standard_wells = sum([self.__well_from_ID(standard_ID, self.__plateLayout) for standard_ID in self.__standard_IDs], [])
        return self.__standard_dict,self.__standard_wells
    def __baselineCorrection(self):
        '''
        this tidies up the absorbance reading
        gives baseline correction and find the linear region for all the wells
        '''
        self.absorbanceSelected = self.__onlyReadWell(self.__absorbanceReading,self.__plateLayout.keys()) # select the non-empty wells in the absorbance
        self.__absorbanceBaselineCorrected = {}
        self.__linearRegion = {}
        self.__blankWells = ['H1','H2'] # correct this one please :D
        for key in self.__plateLayout.keys():
            row_count = len(self.absorbanceSelected[self.__blankWells[0]])
            col_count = len(self.__blankWells)
            blank = np.array([self.__absorbanceReading[self.__blankWells[i]][str(v)] for i in range(0,col_count) for v in range(0,row_count)]).reshape(row_count,col_count).mean(axis=1) # check how to convert the str to int in json
            self.__absorbanceBaselineCorrected[key] = (np.array([self.absorbanceSelected[key][str(i)] for i in range(len(self.absorbanceSelected[key]))]) - blank)
            n = 5
            Second_dev = np.diff(self.__absorbanceBaselineCorrected[key])[5:]
            index_list= np.where(Second_dev<-0.01)[0]
            if len(index_list) == 0:
                index_ = row_count-1
            else:
                index_ = index_list[0] + n
            self.__linearRegion[key] = index_
        return self.__linearRegion, self.__absorbanceBaselineCorrected

    def __calibrationTimeStamp(self):
        self.__linearRegion, self.__absorbanceBaselineCorrected = self.__baselineCorrection()
        self.__standard_dict,self.__standard_wells = self.__standardWells()
        row_time = len(self.__absorbanceBaselineCorrected[self.__blankWells[0]])
        col_conc = len(self.__standard_wells)
        cals = np.zeros([row_time,col_conc])
        concs = []

        for col in range(col_conc):
            OD0 = self.__absorbanceBaselineCorrected[self.__standard_wells[col]][0]
            dODx = self.__absorbanceBaselineCorrected[self.__standard_wells[col]][:] - OD0
            conc = self.__standard_dict[self.__plateLayout[self.__standard_wells[col]]]
            concs.append(conc)
            for row in range(0,row_time):

                cals[row,col] = dODx[row]

        self.__calibration_atTimeStamp = {}
        for time_stamp in range(row_time):
            abs = cals[time_stamp]
            slope, intercept, r_value, p_value, std_err = stats.linregress(concs, abs)
            self.__calibration_atTimeStamp[time_stamp] = {'slope': slope,'intercept': intercept,'LoD': 3 * std_err/slope}

        return self.__calibration_atTimeStamp
    def Results(self):
        result = {}
        self.__calibration_atTimeStamp = self.__calibrationTimeStamp()
        self.__linearRegion, self.__absorbanceBaselineCorrected = self.__baselineCorrection()
        self.__standard_dict,self.__standard_wells = self.__standardWells()
        self.__sample_wells = [well for well in self.__plateLayout.keys() if well not in self.__standard_wells]
        self.__dilution_map = self.__dilutionMapping()
        # print (self.__calibration_atTimeStamp)
        for col in self.__sample_wells:
            sample_ID = self.__plateLayout[col]
            dilution = self.__dilution_map[col]
            linear_region_idx = self.__linearRegion[col] # linear region obtained from the previous step
            DO0 = self.__absorbanceBaselineCorrected[col][0]
            DO1 = self.__absorbanceBaselineCorrected[col][linear_region_idx]
            dDO = DO1 - DO0
            dilution = self.__dilution_map[col]
            linear_region_idx_cali = self.__calibration_atTimeStamp[linear_region_idx]
            # print(linear_region_idx_cali)
            B = (dDO - linear_region_idx_cali['intercept'])/linear_region_idx_cali['slope'] # in (mU/mL) - result from calibraion
            GOx = B * dilution # in [mU/mL]
            activity = GOx * self.__stockVolume/self.__stockGram # in [mU/mg]
            LoD = linear_region_idx_cali['LoD']
            if B > LoD:
                LoD_check = 'pass'
            else:
                LoD_check = 'fail'
            result[col] = {'sample ID': sample_ID,'dDO': dDO, 'calibrated_B' : B, 
                            'GOxConc_in_mUpermL': GOx, 'activity_in_UperL' : activity}

        print (result)
        return abcam_response(GOx_result = result)



    