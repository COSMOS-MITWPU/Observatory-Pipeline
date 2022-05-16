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

allFiles=[f for f in os.listdir('./data-sample/')]
photometryFiles=[]
for file in allFiles:
    if file.endswith('.fits'):
        photometryFiles.append(f'{dir}{file}')



imageName=photometryFiles[0]
f=fits.open(imageName)
data=f[0].data
header=f[0].header
w = WCS(header)

raImage, decImage= w.all_pix2world(data.shape[0]/2, data.shape[1]/2,1)
print(raImage,' ',decImage)


boxsize=30
maxmag=18

Q = [Table.read('data-sample/ps1_v641cyg.tab')]

ps1_imCoords = w.all_world2pix(Q[0]['RAJ2000'], Q[0]['DEJ2000'], 1)
good_cat_stars=Q[0][np.where((ps1_imCoords[0] > 500) & (ps1_imCoords[0] < 3500) & (ps1_imCoords[1] > 500) & (ps1_imCoords[1] < 3500))]
print(good_cat_stars)

# Aperture Photometry

os.chdir('/mnt/d/COSMOS/All_modules/photometry/data')

configFile = 'photomCat.sex'
paramName = 'photomCat.param'

catalogName = photometryFiles[0]+'.cat'

try:
    command = 'source-extractor -c %s %s -CATALOG_NAME %s -PARAMETERS_NAME %s' % (configFile, photometryFiles[0], catalogName, paramName)
    print('Executing command: %s' % command)
    rval = subprocess.run(command.split(), check=True)
except subprocess.CalledProcessError as err:
    print('Could not run sextractor with exit error %s'%err)
frame=1
if frame>0:
    frame = frame*2
tbl = Table.read(catalogName, hdu=frame)
print(tbl)


cleanSources = tbl[(tbl['FLAGS']==0) & (tbl['FWHM_WORLD'] < 2) & (tbl['XWIN_IMAGE']<3500) & (tbl['XWIN_IMAGE']>500) &(tbl['YWIN_IMAGE']<3500) &(tbl['YWIN_IMAGE']>500)]
print(cleanSources)
sourceCatCoords = SkyCoord(ra=cleanSources['ALPHAWIN_J2000'], dec=cleanSources['DELTAWIN_J2000'], frame='icrs', unit='degree')
ps1CatCoords = SkyCoord(ra=good_cat_stars['RAJ2000'], dec=good_cat_stars['DEJ2000'], frame='icrs', unit='degree')

print(sourceCatCoords)

photoDistThresh = 0.6
idx_image, idx_ps1, d2d, d3d = ps1CatCoords.search_around_sky(sourceCatCoords, photoDistThresh*u.arcsec)



# Zero Point deviation
#Apertures in the SExtractor configuration file

aperture_diameter = np.arange(4, 14)

#For each aperture, we are going to compute the magniutde difference between the largest pixel aperture and that specific aperture for every source in cross-matched catalog

magDiff = np.ma.zeros((len(aperture_diameter), len(idx_image)))
for j in range(len(aperture_diameter)):
    magDiff[j] = sigma_clip(cleanSources['MAG_APER'][:,9][idx_image] - cleanSources['MAG_APER'][:,j][idx_image])
    
    #Here, magDiff is a 2D array contaning the difference magnitudes for each source and aperture
print(magDiff) 

zeroPoints = []
for i in range(len(aperture_diameter)):
    #Array of differences between the catalog and instrumental magnitudes
    offsets = ma.array(good_cat_stars['gmag'][idx_ps1] - cleanSources['MAG_APER'][:,i][idx_image])
    #Compute sigma clipped statistics
    zero_mean, zero_med, zero_std = sigma_clipped_stats(offsets)
    zeroDict = {'diameter': aperture_diameter[i], 'zp_mean': zero_mean, 'zp_median': zero_med, 'zp_std': zero_std}
    zeroPoints.append(zeroDict)
    print(zeroDict) 


magFile = photometryFiles[0] + '.apermag.txt'
compMagList = ascii.read(magFile, format = 'no_header', data_start=4)

radii = compMagList['col1']
fluxSums = compMagList['col2']
fluxArea = compMagList['col3']
flux = compMagList['col4']
mags = compMagList['col5']
magErrs = compMagList['col6']


for i in range(len(mags)):
    magCorrected = mags[i] + zeroPoints[i]['zp_median'] - 25
    #IRAF assumes a zero-point of 25 by default, so we've adjusted for that offset here
    magCorrectedErr = np.sqrt(zeroPoints[i]['zp_std']**2 + magErrs[i]**2)
    print('Corrected magnitude of %.2f +/- %.2f for a diameter of %.1f pixels'%(magCorrected, magCorrectedErr, zeroPoints[i]['diameter']))
