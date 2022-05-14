from distutils import filelist
from genericpath import isfile
from random import random
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
from astroquery.vizier import Vizier 
from astropy.table import Table


dir='/mnt/d/Obs_prep/Observatory-Documentation/data-sample/'
dataList=[]
headerList=[]
raImageList=[]
decImageList=[]
catalogNameList=[]
wcs_list=[]
good_cat_stars=[]
tblList=[]
cleanSourcesList=[]

allFiles=[f for f in os.listdir('./data-sample/')]
photometryFiles=[]
for file in allFiles:
    if file.endswith('.fits'):
        photometryFiles.append(f'{dir}{file}')


for i in range (len(photometryFiles)):
    imageName=photometryFiles[i]
    f=fits.open(imageName)
    data=f[0].data
    header=f[0].header

    dataList.append(data)
    headerList.append(header)


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

Q = [Table.read('data-sample/ps1_v641cyg.tab')]

print(len(wcs_list))

for i in range(0,9):
    try:
        ps1_imCoords = wcs_list[i].all_world2pix(Q[0]['RAJ2000'], Q[0]['DEJ2000'], 1)
        good_cat_stars.append(Q[0][np.where((ps1_imCoords[0] > 500) & (ps1_imCoords[0] < 3500) & (ps1_imCoords[1] > 500) & (ps1_imCoords[1] < 3500))])
    except TypeError:
        pass
print(good_cat_stars)

# Aperture Photometry

os.chdir('/mnt/d/COSMOS/All_modules/photometry/data')

configFile = 'photomCat.sex'
paramName = 'photomCat.param'


for i in range(len(photometryFiles)):
    catalogName = photometryFiles[i]+'.cat'
    catalogNameList.append(catalogName)
    try:
        command = 'source-extractor -c %s %s -CATALOG_NAME %s -PARAMETERS_NAME %s' % (configFile, photometryFiles[i], catalogName, paramName)
        print('Executing command: %s' % command)
        rval = subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as err:
        print('Could not run sextractor with exit error %s'%err)

for i in range(len(catalogNameList)):
    frame=1
    if frame>0:
        frame = frame*2
    tbl = Table.read(catalogNameList[0], hdu=frame)
    tblList.append(tbl)

for i in range(len(tblList)):
    cleanSources = tblList[i][(tblList[0]['FLAGS']==0) & (tblList[i]['FWHM_WORLD'] < 2) & (tblList[i]['XWIN_IMAGE']<3500) & (tblList[i]['XWIN_IMAGE']>500) &(tblList[i]['YWIN_IMAGE']<3500) &(tblList[i]['YWIN_IMAGE']>500)]
    cleanSourcesList.append(cleanSources)
print(cleanSourcesList)
