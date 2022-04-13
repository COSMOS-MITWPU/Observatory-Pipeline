from astropy.io import fits
import matplotlib.pyplot as plt
import glob
import os
from astropy.stats import sigma_clipped_stats
import numpy as np
import subprocess
import astroscrappy
import pyregion
import shutil

curpath = os.path.abspath('.')                  
dataFolder = os.path.join(curpath, 'data')      
biasFolder = os.path.join(dataFolder, 'bias')   
flatFolder = os.path.join(dataFolder, 'flats')  
sciFolder = os.path.join(dataFolder, 'science') 
procFolder = os.path.join(curpath, 'processing')
if not os.path.isdir(procFolder): 
    os.mkdir(procFolder)
else:
    for f in os.listdir(procFolder):
        os.remove(os.path.join(procFolder,f)) #clear the processing folder from previous iterations

os.chdir(sciFolder)
fileList = glob.glob('*.fits')
os.chdir(curpath)
procList = [os.path.join(procFolder, file) for file in fileList]
sciList = [os.path.join(sciFolder, file) for file in fileList]


def masterBiasFrame(biasFolder):
    biasList = glob.glob(os.path.join(biasFolder,'*fits'))
    numBiasFiles = len(biasList)
    biasImages = np.zeros((4108, 4096, numBiasFiles))
    for i in range(numBiasFiles):
        biasImages[:,:,i] = fits.open(biasList[i])[0].data
    masterBias = np.median(biasImages, axis=2)
    return masterBias

# print(masterBiasFrame(biasFolder)) # testing

def flatFrame(flatFolder):
    flatList=glob.glob(os.path.join(flatFolder, '*fits'))
    numFlatFiles=len(flatList)
    flatImages = np.zeros((4108, 4096, numFlatFiles))
    for i in range(numFlatFiles):
        #subtract the master bias and store the flat field image
        flatImages[:,:,i] = fits.open(flatList[i])[0].data - masterBiasFrame(biasFolder)
        flatImages[:,:,i] = flatImages[:,:,i] / np.median(flatImages[:,:,i])
    return flatImages

# print(flatFrame(flatFolder)) # Testing


