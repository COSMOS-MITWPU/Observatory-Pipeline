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

os.chdir(sciFolder)
fileList = glob.glob('*.fits')
os.chdir(curpath)
procList = [os.path.join(procFolder, file) for file in fileList]
sciList = [os.path.join(sciFolder, file) for file in fileList]



def astrometricCalibration(dataFolder,procFolder,sciList):
    autoastrometry_script=os.path.join(dataFolder, 'autoastrometry.py')
    os.chdir(procFolder)
    numSciFiles=len(sciList)
    print('supposed to make a files here')
    for i in range(1, numSciFiles):
        try:
            filelist = procList[i]+'.proc.cr.fits'
            command = 'python %s %s -c tmc' % (autoastrometry_script, filelist)
            print('Executing command: %s' % command)
            rval = subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as err:
            print('Could not run autoastrometry with error %s. Check if file exists.'%err)
    print("DONE !")

astrometricCalibration(dataFolder, procFolder, sciList)