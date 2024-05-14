#Libraries
import skimage
import skimage.io
import skimage.filters
import skimage.color
import pandas as pd
import numpy as np


class FeatureDetector():

    def __init__(self):
        self.__imgPath = './TestImg/TestImg.jpg' #default Img path
        self.__sigma = 5 #Sigma for gaussian smoothing
        self.__smoothing = True #Boolean for applying smoothing or not
        self.__maxNOfPixelToProcess = 125000 # to rescale max number of pixel to ease out overheads 
        pass

    #Getters
    def ImgPath(self):
        return self.__imgPath

    def Sigma(self):
        return self.__sigma

    def Smoothing(self):
        return self.__smoothing

    def maxNOfPixelToProcess(self):
        return self.__maxNOfPixelToProcess

    #Setters
    def SetImgPath(self, x):
        self.__imgPath = x
        pass

    def SetSigma(self, x):
        self.__sigma = x
        pass

    def SetSmoothing(self, x):
        self.__smoothing = x
        pass

    def SetMaxNOfPixel(self, x):
        self.__maxNOfPixelToProcess = x
        pass

    #Helper functions
    def ReadImg(self):
        return skimage.io.imread(self.__imgPath)

    def SmoothImg(self, img):
        return skimage.filters.gaussian(img, self.__sigma)

    def ImgROI(self, img):
        grayImg = skimage.color.rgb2gray(img)
        threshold = skimage.filters.threshold_otsu(grayImg)
        return grayImg < threshold

    def HSVImg(self, img):
        return skimage.color.rgb2hsv(img)

    def ExtractFeatures(self, imgROI, hsvImg): #Code for extracting the hue, saturation and value of the ROI in the image
# =============================================================================
         # '''
         # # need to use internal library to do following task..
         # # slowing down code if image is big and therefore phone dependent
         # '''
# =============================================================================
        hue = []
        saturation = []
        value = []
        shape = np.array(imgROI).shape
        for row in range(shape[0]):
            for column in range(shape[1]):
                if imgROI[row, column]:
                    hue.append(hsvImg[row, column, 0])
                    saturation.append(hsvImg[row, column, 1])
                    value.append(hsvImg[row, column, 2])
        result = pd.DataFrame()
        result['Hue'] = hue
        result['Saturation'] = saturation
        result['Value'] = value
        return result

    def Setup(self, imgPath, sigma, smoothing,maxNOfPixel): #Code for setting up the feature detector
        self.SetImgPath(imgPath)
        self.SetSigma(sigma)
        self.SetSmoothing(smoothing)
        self.SetMaxNOfPixel(maxNOfPixel)
        pass

    def Process(self): #Code for processing image and extracting features into a pd.DataFrame() Object
        img = self.ReadImg()
        if self.__smoothing:
            img = self.SmoothImg(img)
        imgROI = self.ImgROI(img)
        hsvImg = self.HSVImg(img)
        return self.ExtractFeatures(imgROI, hsvImg)
    pass
