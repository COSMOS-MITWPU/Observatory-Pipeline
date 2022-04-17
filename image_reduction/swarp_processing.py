from audioop import bias
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


# print(curpath)
# print(dataFolder)
# print(biasFolder)
# print(flatFolder)
# print(sciFolder)
# print(procFolder)

os.chdir(sciFolder)
fileList = glob.glob('*.fits')
os.chdir(curpath)
procList = [os.path.join(procFolder, file) for file in fileList]
sciList = [os.path.join(sciFolder, file) for file in fileList]

numSciFiles=len(sciList)

swarpFileList = os.path.join(procFolder, 'swarpFileList.txt')
f = open(swarpFileList, 'w')
for i in range(1,numSciFiles):
    f.write(os.path.join(procFolder, 'a'+fileList[i]+'.proc.cr.fits\n'))
f.close()

def make_swarp_command(swarpConfigFile, procFolder, how_do_you_call_swarp): 
    swarpFileList = os.path.join(procFolder, 'swarpFileList.txt')
    new_file_names = []
    
    # extracting the list and making the command
    with open(os.path.join(procFolder, 'swarpFileList.txt'), 'r+') as f:
        file_names = f.readlines()
        
    for i in file_names[:]:
        new_file_names.append(i.strip('\n'))

    # merging the list into a single string
    input_files = ' '.join(new_file_names)
    command = f'{how_do_you_call_swarp} {input_files} -c {swarpConfigFile}'
    with open('./new.txt', 'w') as f:
        f.write(command)
        
    return command

def swarpConfig(dataFolder,sciList):
    swarpConfigFile = os.path.join(dataFolder, 'stack.swarp')

    # f = open(swarpFileList, 'w')
    # for i in range(numSciFiles):
    #     f.write(os.path.join(procFolder, 'a'+fileList[i]+'.proc.cr.fits\n'))
    # f.close()
    
    try:
        # Make a text file listing the images to be stacked to feed into swarp
        command = make_swarp_command(swarpConfigFile, procFolder, 'SWarp')
        print("Executing command: %s" % command)
        print(command)
        subprocess.run(command, shell=True)
    except:
        print('trying another way to call SWarp')
        command = make_swarp_command(swarpConfigFile, procFolder, 'SWarp')
        print("Executing command: %s" % command)
        print(command)
        subprocess.run(command, shell=True)
    print(os.getcwd())


swarpConfig(dataFolder,sciList)
