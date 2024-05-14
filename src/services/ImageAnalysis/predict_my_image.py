# -*- coding: utf-8 -*-
"""
Created on Sun Nov 21 13:13:51 2021

@author: kensl
"""
# load libraries
import joblib
from .feature_detection import FeatureDetector
import numpy as np


class predict_my_image():
    def __init__(self):
        self.__TrainModelPath = '../TrainedModel/20211121/20211121_model_standardScaler_quadDA.sav' #'../TrainedModel/20211121/20211121_model_standardScaler_quadDA.sav'         # path to saved model
        self.__ImageToReadPath = '../Images/Baked_Cropped/20211119_DT_back1_good.jpg'                       # path to dummy image if not specified
        self.__maxNumberOfPixel = 125000            # to rescale max number of pixel to ease out overheads
        self.__GaussianSigma  = 3                   # Sigma for gaussian smoothing
        self.__GaussianSmoothing = True             # Boolean for applying Gaussian smoothing or not
        self.__BurntThreshold = 0.5                 # threshold to say whether cookie is burnt or not
    #Getters
    def TrainModelPath(self):
        return self.__TrainModelPath

    def ImageToReadPath (self):
        return self.__ImageToReadPath

    def maxNOfPixelToProcess(self):
        return self.__maxNumberOfPixel

    def GaussianSigma(self):
        return self.__GaussianSigma

    def GaussianSmoothing(self):
        return self.__GaussianSmoothing

    def BurntThreshold(self):
        return self.__BurntThreshold

    #Setters
    def SetTrainModelPath(self, x):
        self.__TrainModelPath = x
        pass

    def SetImageToReadPath(self, x):
        self.__ImageToReadPath = x
        pass

    def SetMaxNOfPixel(self, x):
        self.__maxNumberOfPixel = x
        pass

    def SetGaussianSigma(self, x):
        self.__GaussianSigma = x
        pass

    def SetGaussianSmoothing(self, x):
        self.__GaussianSmoothing = x
        pass

    def SetBurntThreshold(self, x):
        self.__BurntThreshold = x
        pass

    #Helper functions
    def Setup(self, trainModelPath, imagePath,maxNumberOfPixel,GaussianSigma,GaussSmoothBool,burntThreshold): #Code for setting up the feature detector
        self.SetTrainModelPath(trainModelPath)
        self.SetImageToReadPath(imagePath)
        self.SetMaxNOfPixel(maxNumberOfPixel)
        self.SetGaussianSigma(GaussianSigma)
        self.SetGaussianSmoothing(GaussSmoothBool)
        self.SetBurntThreshold(burntThreshold)
        pass

    def loadMyModel(self):
        return joblib.load(self.__TrainModelPath)

    def ExtractFeatures(self):
        featureDetector = FeatureDetector()
        featureDetector.Setup(self.__ImageToReadPath ,self.__GaussianSigma, self.__GaussianSmoothing,self.__maxNumberOfPixel)
        return featureDetector.Process()

    def Process(self):
        featuresFromImg = self.ExtractFeatures()  # process image to obtain image
        loadSavedModel =  self.loadMyModel() # load saved model
        myModel = loadSavedModel['myModel']
        standardiseMyData = loadSavedModel['standardiseMyData']
        meanPrediction = np.mean(myModel.predict(standardiseMyData.transform(np.array(featuresFromImg))))

        threshold = self.__BurntThreshold
        if meanPrediction<threshold:
            returnString = 'Not Burnt'
        else:
            returnString = 'Burnt'

        return returnString
