# -*- coding: utf-8 -*-
"""
Created on Sun Nov 21 14:01:55 2021

@author: kensl
"""

# script calling image and predict using saved model
from .predict_my_image import predict_my_image
import os

# 20211119_CC_front3_good.jpg
def predict(ImageToReadPath):
  absPath = os.path.dirname(os.path.realpath(__file__))
  # define inputs
  TrainedModelPath = os.path.join(absPath,'20211121_model_standardScaler_quadDA.sav')
  #TrainedModelPath =  os.path.join(relpath,'TrainedModel/20211121/20211121_model_standardScaler_quadDA.sav')
  maxNOfPixel = 125000
  GaussianSigma =  3
  GaussSmoothBool = True
  burntThreshold = 0.125

  # set your names for functions
  callMyPredictionModel =  predict_my_image()

  # call function
  callMyPredictionModel.Setup(TrainedModelPath, ImageToReadPath, maxNOfPixel, GaussianSigma, GaussSmoothBool,burntThreshold)
  return callMyPredictionModel.Process() # print outcome - burnt or not burnt
