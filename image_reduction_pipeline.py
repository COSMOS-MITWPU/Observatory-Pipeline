from doctest import master
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

def masterFlatFrame(flatFolder):
    flatList=glob.glob(os.path.join(flatFolder, '*fits'))
    numFlatFiles=len(flatList)
    flatImages = np.zeros((4108, 4096, numFlatFiles))
    for i in range(numFlatFiles):
        #subtract the master bias and store the flat field image
        flatImages[:,:,i] = fits.open(flatList[i])[0].data - masterBiasFrame(biasFolder)
        flatImages[:,:,i] = flatImages[:,:,i] / np.median(flatImages[:,:,i])
    masterFlat=np.mean(flatImages,axis=2)
    return masterFlat
# print(masterFlatFrame(flatFolder)) # Testing

def processingData(sciList):
    numSciFiles=len(sciList)
    for i in range(numSciFiles):
        rawHDU=fits.open(sciList[i])[0]
        rawData=rawHDU.data
        rawHeader=rawHDU.header
        # Bias and flat correction
        procData=rawData-masterBiasFrame(biasFolder)/masterFlatFrame(flatFolder)
        procHDU=fits.PrimaryHDU(procData)
        procHDU.header=rawHeader
        procHDU.header.remove('BZERO')
        procHDU.header.remove('BSCALE')
        procHDU.writeto(procList[i]+'.proc.fits', overwrite=True)

def cosmicCorrection(sciList):
        detectorGain = 1.6 #in e-/ADU
        readNoise = 14.0 #in electrons
        saturLevel = 150000 #in electrons

        numSciFiles=len(sciList)

        for i in range(1,numSciFiles):
            procHDU=fits.open(procList[i]+'.proc.fits')[0]
            procData=procHDU.data
            procHeader=procHDU.header

            crmask,cleanArray=astroscrappy.detect_cosmics(procData,gain=detectorGain,readnoise=readNoise,satlevel=saturLevel)

            procData_cr = cleanArray / detectorGain
            crCleanHDU = fits.PrimaryHDU(procData_cr)
            crCleanHDU.header = procHeader
            crCleanHDU.writeto(procList[i] +'.proc.cr.fits', overwrite=True)
        print("DONE !")

def astrometricCalibration(dataFolder,procFolder,sciList):
    autoastrometry_script=os.path.join(dataFolder, 'autoastrometry.py')
    os.chdir(procFolder)
    numSciFiles=len(sciList)
    for i in range(1, numSciFiles):
        try:
            filelist = procList[i]+'.proc.cr.fits'
            command = 'python %s %s -c tmc' % (autoastrometry_script, filelist)
            print('Executing command: %s' % command)
            rval = subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as err:
            print('Could not run autoastrometry with error %s. Check if file exists.'%err)
    print("DONE !")

def swarpConfig(dataFolder,sciList):
    numSciFiles=len(sciList)
    swarpConfigFile = os.path.join(dataFolder, 'stack.swarp')

    #Make a text file listing the images to be stacked to feed into swarp
    swarpFileList = os.path.join(procFolder, 'swarpFileList.txt')
    f = open(swarpFileList, 'w')
    for i in range(numSciFiles):
        f.write(os.path.join(procFolder, 'a'+fileList[i]+'.proc.cr.fits\n'))
    f.close()

    try:
        #IMAGEOUT_NAME is the output stackd file, WEIGHTOUT_NAME is the output weight file, RESAMPLE_DIR is the directory where the resampled images are to be stored
        command = 'SWarp -c %s @%s -IMAGEOUT_NAME V641Cyg_g_stack.fits -WEIGHTOUT_NAME V641Cyg_g_stack.weight.fits -RESAMPLE_DIR %s' % (swarpConfigFile, swarpFileList, procFolder)
        print("Executing command: %s" % command)
        rval = subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as err:
        print('Could not run swarp. Can you run it from the terminal?')
    print(os.getcwd())

processingData(sciList)
cosmicCorrection(sciList)
astrometricCalibration(dataFolder,procFolder,sciList)
swarpConfig(dataFolder,sciList)
# The functions have to be run in this order 
