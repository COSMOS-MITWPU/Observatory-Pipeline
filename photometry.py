from distutils import filelist
from genericpath import isfile
import numpy as np
import numpy.ma as ma
import os
from os.path import isfile, join
import astropy.units as u
from astropy.io import ascii
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.stats import sigma_clipped_stats, sigma_clip
import subprocess
import glob
import re
from astropy.io import fits
import matplotlib.pyplot as plt

dir='/mnt/d/Obs_prep/Observatory-Documentation/data-sample/'
dataList=[]
headerList=[]
raImageList=[]
decImageList=[]


allFiles=[f for f in os.listdir('./data-sample/')]
photometryFiles=[]
for file in allFiles:
    if file.endswith('.fits'):
        photometryFiles.append(f'{dir}{file}')

photometryFiles.pop(1)
for i in photometryFiles:   
    print(i)

# imageName=photometryFiles[0]
# f=fits.open(imageName)

# data=f[0].data
# header=f[0].header


for i in range (len(photometryFiles)):
    imageName=photometryFiles[i]
    f=fits.open(imageName)
    data=f[0].data
    header=f[0].header

    dataList.append(data)
    headerList.append(header)

wcs_list=[]
for i in range (len(headerList)):
    wcs_list.append(WCS(headerList[i]))

for i in range(len(headerList)):
    raImage, decImage= wcs_list[0].all_pix2world(dataList[i].shape[0]/2, dataList[i].shape[1]/2,1)
    raImageList.append(raImage)
    decImageList.append(decImage)
    
for i in range(len(raImageList)):
    print(raImageList[i],',',decImageList[i])

boxsize=30
maxmag=18
