from distutils import filelist
from email.mime import image
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
import pandas as pd

dir='/mnt/d/Obs_prep/Observatory-Documentation/data-sample/'
imageName='/mnt/d/Obs_prep/Observatory-Documentation/aC0_20181013-183430-709.wcs.fits.proc.cr.resamp.fits'

def get_table_from_ldac(filename, frame=1):
    if frame>0:
        frame = frame*2
    tbl = Table.read(filename, hdu=frame)
    return tbl



def open_fits(imageName):
    f = fits.open(imageName)
    data = f[0].data  
    header = f[0].header
    #Compute some image statistics for scaling the image plot
    mean, median, sigma = sigma_clipped_stats(data) 
    return f,data,header

f,data,header=open_fits(imageName)

 
def create_wcs(data,header):
    #strong the image WCS into an object
    w = WCS(header)
    #Get the RA and Dec of the center of the image
    [raImage, decImage] = w.all_pix2world(data.shape[0]/2, data.shape[1]/2, 1)
    #Set the box size to search for catalog stars
    boxsize = 30 # arcminutes
    #Magnitude cut-offs of sources to be cross-matched against
    maxmag = 18
    return w,boxsize,maxmag,raImage,decImage

w,boxsize,maxmag,raImage,decImage=create_wcs(data,header)


def catalog_quering(raImage,decImage,boxsize,maxmag):
#     global Q
    #Vizier.VIZIER_SERVER = 'vizier.ast.cam.ac.uk'
    catNum = 'II/349'#This is the catalog number of PS1 in Vizier
    print('\nQuerying Vizier %s around RA %.4f, Dec %.4f with a radius of %.4f arcmin'%(catNum, raImage, decImage, boxsize))
    #You can set the filters for the individual columns (magnitude range, number of detections) inside the Vizier query
    v = Vizier(columns=['*'], column_filters={"rmag":"<%.2f"%maxmag, "Nd":">6", "e_Rmag":"<1.086/3"}, row_limit=-1)
    Q = v.query_region(SkyCoord(ra = raImage, dec = decImage, unit = (u.deg, u.deg)), radius = str(boxsize)+'m', catalog=catNum, cache=False)
    #query vizier around (ra, dec) with a radius of boxsize
    #print(Q[0])
    return Q[0]

Q1=catalog_quering(raImage,decImage,boxsize,maxmag)

def wld_coord_2_img_coord(w,Q1):
    #Convert the world coordinates of these stars to image coordinates
    ps1_imCoords = w.all_world2pix(Q1['RAJ2000'], Q1['DEJ2000'], 1)

    #Another round of filtering where we reject sources close to the edges
    good_cat_stars = Q1[np.where((ps1_imCoords[0] > 500) & (ps1_imCoords[0] < 3500) & (ps1_imCoords[1] > 500) & (ps1_imCoords[1] < 3500))]
    return ps1_imCoords, good_cat_stars

ps1_imCoords,good_cat_stars=wld_coord_2_img_coord(w,Q1)

os.chdir('/mnt/d/COSMOS/All_modules/photometry/data')

def source_ext(imageName):
    configFile = 'photomCat.sex'
    catalogName = imageName+'.cat'
    paramName = 'photomCat.param'
    try:
        command = 'source-extractor -c %s %s -CATALOG_NAME %s -PARAMETERS_NAME %s' % (configFile, imageName, catalogName, paramName)
        print('Executing command: %s' % command)
        rval = subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as err:
        print('Could not run sextractor with exit error %s'%err)
    return configFile,catalogName,paramName


def get_table_from_ldac(filename, frame=1):
    """
    Load an astropy table from a fits_ldac by frame (Since the ldac format has column 
    info for odd tables, giving it twce as many tables as a regular fits BinTableHDU,
    match the frame of a table to its corresponding frame in the ldac file).
    

    Parameters
    ----------
    filename: str
        Name of the file to open
    frame: int
        Number of the frame in a regular fits file
    """
    from astropy.table import Table
    if frame>0:
        frame = frame*2
    tbl = Table.read(filename, hdu=frame)
    return tbl

configFile,catalogName,paramName = source_ext(imageName)

source_table=get_table_from_ldac(catalogName)

# #filter on the sources to select the ones satisfying our criteria
def cln_srcs(sourceTable):
    cleanSources = sourceTable[(sourceTable['FLAGS']==0) & (sourceTable['FWHM_WORLD'] < 2) & (sourceTable['XWIN_IMAGE']<3500) & (sourceTable['XWIN_IMAGE']>500) &(sourceTable['YWIN_IMAGE']<3500) &(sourceTable['YWIN_IMAGE']>500)]
    return cleanSources




def psf_ex(catalogName):
    psfConfigFile = 'psfex_conf.psfex'
    try:
        command = 'psfex -c %s %s' % (psfConfigFile, catalogName)
        print('Executing command: %s' % command)
        rval = subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as err:
        print('Could not run psfex with exit error %s'%err)
    return psfConfigFile

 

def psf_model(imageName):
    psfModelHDU = fits.open(imageName)[0]
    psfModelData = psfModelHDU.data
    mean, median, std = sigma_clipped_stats(psfModelData)
    return psfModelData
 

def point_src_psf(configFile,imageName):
    psfName = imageName + '.psf'
    psfcatalogName = imageName+'.psf.cat'
    psfparamName = 'photomPSF.param' #This is a new set of parameters to be obtained from SExtractor, including PSF-fit magnitudes
    try:
        #We are supplying SExtactor with the PSF model with the PSF_NAME option
        command = 'source-extractor -c %s %s -CATALOG_NAME %s -PSF_NAME %s -PARAMETERS_NAME %s' % (configFile, imageName, psfcatalogName, psfName, psfparamName)
        print("Executing command: %s" % command)
        rval = subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as err:
        print('Could not run sextractor with exit error %s'%err)
    return psfName, psfcatalogName, psfparamName    

 


def cln_src_psf(psfsourceTable):
#Selecting the clean sources away from image edges as before 
    cleanPSFSources = psfsourceTable[(psfsourceTable['FLAGS']==0) & (psfsourceTable['FLAGS_MODEL']==0)  & (psfsourceTable['FWHM_WORLD'] < 2) & (psfsourceTable['XMODEL_IMAGE']<3500) & (psfsourceTable['XMODEL_IMAGE']>500) &(psfsourceTable['YMODEL_IMAGE']<3500) &(psfsourceTable['YMODEL_IMAGE']>500)]
    return cleanPSFSources

 

def catalog_cross_matching(cleanPSFSources,good_cat_stars):
    psfsourceCatCoords = SkyCoord(ra=cleanPSFSources['ALPHAWIN_J2000'], dec=cleanPSFSources['DELTAWIN_J2000'], frame='icrs', unit='degree')
    ps1CatCoords = SkyCoord(ra=good_cat_stars['RAJ2000'], dec=good_cat_stars['DEJ2000'], frame='icrs', unit='degree')
    #Now cross match sources
    #Set the cross-match distance threshold to 2 arcsec, or just about one pixel
    photoDistThresh = 2.1
    idx_psfimage, idx_psfps1, d2d, d3d = ps1CatCoords.search_around_sky(psfsourceCatCoords, photoDistThresh*u.arcsec)
    return psfsourceCatCoords, ps1CatCoords, idx_psfimage, idx_psfps1, photoDistThresh
#print('Found %d good cross-matches'%len(idx_psfimage))
    
 

def psf_off_set(good_cat_stars,idx_psfps1,idx_psfimage,cleanPSFSources):
    psfoffsets = ma.array(good_cat_stars['rmag'][idx_psfps1] - cleanPSFSources['MAG_POINTSOURCE'][idx_psfimage])
    #Compute sigma clipped statistics
    zero_psfmean, zero_psfmed, zero_psfstd = sigma_clipped_stats(psfoffsets)
    return zero_psfmean, zero_psfmed, zero_psfstd
    #print('PSF Mean ZP: %.2f\nPSF Median ZP: %.2f\nPSF STD ZP: %.2f'%(zero_psfmean, zero_psfmed, zero_psfstd))

 


def desired_src(photoDistThresh,psfsourceCatCoords):
    ra = 186.550292
    dec = 58.314119

    SN2018hna_coords = SkyCoord(ra=[ra], dec=[dec], frame='icrs', unit='degree')
    idx_SN2018hna, idx_cleanpsf_SN2018hna, d2d, d3d = psfsourceCatCoords.search_around_sky(SN2018hna_coords, photoDistThresh*u.arcsec)
    return SN2018hna_coords, idx_SN2018hna, idx_cleanpsf_SN2018hna  
# #  print('Found the source at index %d'%idx_cleanpsf_SN2018hna[0])


def desired_src_mag(cleanPSFSources,idx_cleanpsf_SN2018hna,zero_psfmed,zero_psfstd):
    SN2018hna_psfinstmag = cleanPSFSources[idx_cleanpsf_SN2018hna]['MAG_POINTSOURCE'][0]
    SN2018hna_psfinstmagerr = cleanPSFSources[idx_cleanpsf_SN2018hna]['MAGERR_POINTSOURCE'][0]

    SN2018hna_psfmag = zero_psfmed + SN2018hna_psfinstmag
    SN2018hna_psfmagerr = np.sqrt(SN2018hna_psfinstmagerr**2 + zero_psfstd**2)
    return SN2018hna_psfmag, SN2018hna_psfmagerr



def main():
    os.chdir('/mnt/d/Obs_prep/Observatory-Documentation/data-sample/')

    imageName="/mnt/d/COSMOS/All_modules/photometry/data/aC0_20181013-174714-557.wcs.fits.proc.cr.fits"
    # /mnt/d/Obs_prep/Observatory-Documentation/aC0_20181013-183430-709.wcs.fits.proc.cr.resamp.fits.homo.fits
   
    curpath = os.path.abspath('.')
    dataFolder = os.chdir('/mnt/d/Obs_prep/Observatory-Documentation/data-sample/')
    outputFolder = os.chdir('/mnt/d/Obs_prep/Observatory-Documentation/outputs')
    os.chdir('/mnt/d/Obs_prep/Observatory-Documentation/data-sample/')
    file_list = glob.glob("*.fits")
    os.chdir('/mnt/d/Obs_prep/Observatory-Documentation/outputs')
    df = pd.DataFrame({'Image': [],
                    'JD' : [],
                    'PSF_Mag' : [],
                    'PSF_MagErr' : []})
    
    for file in file_list[:5]:
        imageName = file
        f,data,header = open_fits(imageName)   
        w,boxsize,maxmag,raImage,decImage = create_wcs(data,header)
        Q1 = catalog_quering(raImage,decImage,boxsize,maxmag)
        ps1_imCoords, good_cat_stars = wld_coord_2_img_coord(w,Q1)
        configFile,catalogName,paramName = source_ext(imageName)
        sourceTable = get_table_from_ldac(catalogName)
        cleanSources = cln_srcs(sourceTable)
        psfConfigFile = psf_ex(catalogName)
        psfModelData = psf_model(imageName)
        psfName, psfcatalogName, psfparamName = point_src_psf(configFile,imageName)
        psfsourceTable = get_table_from_ldac(psfcatalogName)
        cleanPSFSources = cln_src_psf(psfsourceTable)
        psfsourceCatCoords, ps1CatCoords, idx_psfimage, idx_psfps1, photoDistThresh = catalog_cross_matching(cleanPSFSources,good_cat_stars)
        zero_psfmean, zero_psfmed, zero_psfstd = psf_off_set(good_cat_stars,idx_psfps1,idx_psfimage,cleanPSFSources)
        SN2018hna_coords, idx_SN2018hna, idx_cleanpsf_SN2018hna = desired_src(photoDistThresh,psfsourceCatCoords)
        SN2018hna_psfmag, SN2018hna_psfmagerr = desired_src_mag(cleanPSFSources,idx_cleanpsf_SN2018hna,zero_psfmed,zero_psfstd)
        df2 = pd.DataFrame({'Image':[imageName],
                    'JD' : [header["JD"]],
                    'PSF_Mag' : [SN2018hna_psfmag],
                    'PSF_MagErr' : [SN2018hna_psfmagerr]})  
        df = df.append(df2)
        print(df)
    return df

table=main()

print(table)
