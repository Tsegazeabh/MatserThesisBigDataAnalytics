import os, sys, json
from base64 import urlsafe_b64encode
from fastapi.testclient import TestClient
import glob 
import pandas as pd
import json

# We need to include this so we can read the scr files
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import main
import common.constants


client = TestClient(main.app)

ROOT_URL = common.constants.ROOT_URL
# def test_impedace_circuit_draw():
#     resp = client.get(f"{ROOT_URL}/drawCircuit/R0-p(C1,R1)")
#     assert resp.status_code == 200
#     resp_data = resp.json()
#     assert len(resp_data['warnings']) == 0
#     assert resp_data['success'] == True
#     assert len(resp_data['dataGraph']['data']) == 7998

# def test_impedace_circuit_draw_raw():
#     resp = client.get(f"{ROOT_URL}/drawCircuitRaw/R0-p(C1,R1)")
#     assert resp.status_code == 200
#     resp_data = resp.json()
#     assert len(resp_data['draw']) == 7998

# def test_open_dt6():
#     with open('test/files/test_dt6.dt6','rb') as f:
#         files = {'file': f.read()}
#     resp = client.post(f"{ROOT_URL}/openDT6", files=files)
#     assert resp.status_code == 200
#     resp_data = resp.json()
#     assert len(resp_data['warnings']) == 0
#     assert resp_data['success'] == True
#     assert len(resp_data['dataGraph']['extracted_data']) == 1
#     assert len(resp_data['dataGraph']['extracted_data'][0]['X']) == 726

def test_cookies_prediction_bit64():
    with open("test/files/baked_good.jpg", "rb") as binary_file:
        picture_bytes = urlsafe_b64encode(binary_file.read())
        picture_bit64 = "data:image/jpg;base64," + picture_bytes.decode('ascii')

    data = {'data': picture_bit64}
    resp = client.post(f"{ROOT_URL}/imageRecognitionFromBit64", json=data)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert len(resp_data['warnings']) == 0
    assert resp_data['data']['prediction'] == 'Not Burnt'

def test_standard_addition():
    data = {'Cstd': 150, 'vflask': 50, 'vunk' : 10, 'vadd' : [0, 10, 15, 20, 25], 'mean': [1.31, 9.562, 15.339, 20.635, 24.464]}
    resp = client.post(f"{ROOT_URL}/standardAddition", json=data)
    assert resp.status_code == 200
    resp_data = resp.json()
    # assert resp_data['st_add'] == 15.083815563106906

def test_candy_prediction():
    files = glob.glob('test/files/CandyTestData/test1/*.csv')
    item_dic = {}
    for file in files:
        fname = file.split('/')[-1].split('.')[0]
        df = pd.read_csv(file, skiprows=1)
        df_selected = df.iloc[:,:]
        x = list(df_selected.iloc[:,0].values)
        y = list(df_selected.iloc[:,1].values)
        item_dic[fname] = {'x': x, 'y': y}
    resp = client.post(f"{ROOT_URL}/candyPrediction", json=item_dic)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data['results'][0]['value'] == 0.236
    assert resp_data['results'][1]['value'] == 0.0741


def test_GOx_Abcam():
    item_dic = {}
    with open('test/files/GOxAbcamTestData/wells_mapping.json') as plate_file:
        item_dic['plateLayout'] = json.load(plate_file)
    with open('test/files/GOxAbcamTestData/kinetic_absorbance.json') as abs_file:
        item_dic['absorbanceReading'] = json.load(abs_file)
    with open('test/files/GOxAbcamTestData/kinetic_time.json') as time_file:
        item_dic['timeReading'] = json.load(time_file)
    item_dic['stockVolume'] = 0.5
    item_dic['stockGram'] = 5
    item_dic['dilutionID'] = ['D1','D2']
    item_dic['dilutionFactor'] = [250000,500000]
    item_dic['bottleActivity'] = 248000
    # print (item_dic)
    resp = client.post(f"{ROOT_URL}/GOxAbcam", json=item_dic)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data['GOx_result']['A3']['dDO'] ==  0.585


def test_InfectoTest():
    item_dic = {}
    with open('test/files/InfectoTestData/2077_base.json') as baseFile:
        item_dic['baseFile'] = json.load(baseFile)
    with open('test/files/InfectoTestData/2077_sample.json') as sample_file:
        item_dic['sampleFile'] = json.load(sample_file)
    item_dic['unit'] = 'uA'
    item_dic['slope'] = 4.37e-8
    item_dic['intercept'] = 8.96e-10

    # print (item_dic)
    resp = client.post(f"{ROOT_URL}/InfectoTest", json=item_dic)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data['results'][0]['value'] == 0.61