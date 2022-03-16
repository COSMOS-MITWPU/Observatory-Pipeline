from jinja2 import clear_caches
import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy.coordinates import EarthLocation
import pytz
from astroplan import Observer, FixedTarget
from astropy.utils.iers import conf

conf.auto_max_age = None
from astroplan import download_IERS_A
from astropy.coordinates import get_sun, get_moon, get_body
from astroplan import moon_illumination
from astroplan.plots import plot_finder_image
from astroquery.skyview import SkyView
download_IERS_A()
import pandas as pd
import math

now = Time.now()

from astropy.table import QTable
import astropy.units as u
import numpy as np

import os.path
from os import path
 
def time_in_india():
    date = now + 5 * u.h + 30 * u.min
    return date


def observatory_setup():
    longitude = "73d48m53s"
    latitude = "18d31m7s"
    elevation = 560 * u.m
    location = EarthLocation(longitude, latitude, elevation)
    
    ioMIT = Observer(
        location=location,
        timezone="Asia/Kolkata",
        name="MIT-Telescope",
        description="GSO-Newtonian Telescope MIT World Peace University",
    )
    return ioMIT


def sunset(observatory):
    sunset_ioMIT = observatory.sun_set_time(now, which="nearest")
    return sunset_ioMIT


    
def evening_twilight(observatory):
    eve_twil_ioMIT = observatory.twilight_evening_astronomical(now, which="nearest")
    return eve_twil_ioMIT


def midnight(observatory):
    midnight_ioMIT = observatory.midnight(now, which="nearest")
    return midnight_ioMIT


def morn_twilight(observatory):
    morn_twil_ioMIT = observatory.twilight_morning_astronomical(now, which="nearest")
    return morn_twil_ioMIT

def sunrise(observatory):
    sunrise_ioMIT = observatory.sun_rise_time(now, which='next')
    return sunrise_ioMIT

def local_sidereal_time_now (observatory):
    lst_now = observatory.local_sidereal_time(now)
    return lst_now
    
def local_sidereal_time_midnight(observatory):
    midnight_ioMIT = observatory.midnight(now, which="nearest")
    lst_mid = observatory.local_sidereal_time(midnight_ioMIT)
    return lst_mid
 


observatory = observatory_setup()
class InformationObjects:
    def __init__(self,coord1,coord2,celsobj):
        self.coord1 = coord1
        self.coord2 = coord2
        self.celsobj = celsobj
         
    
 
    
    @property
    def checking_mid_twilight(self): 
        coords = SkyCoord(self.coord1,self.coord2, frame = 'icrs')
        object = FixedTarget(name = self.celsobj, coord = coords)
        eve_twi = observatory.target_is_up(evening_twilight(observatory),object)
        midnit = observatory.target_is_up(midnight(observatory),object)
        morn_twi = observatory.target_is_up(morn_twilight(observatory),object)
        data1 = {"Evening Twilight" : eve_twi, 
                "Midnight" : midnit,
                 "Morning Twilight": morn_twi
                }
        
        return data1
 

    @property
    def rise_times(self):
        coords = SkyCoord(self.coord1,self.coord2, frame = 'icrs')
        object = FixedTarget(name = self.celsobj, coord = coords)
        objectrise = observatory.target_rise_time(now, object , which = 'nearest', horizon = 0 * u.deg)
        with open('dataset.txt', 'a') as f:
            f.write(f"                {objectrise.iso}")
        return  objectrise.iso
    
    @property
    def ra_dec(self):
        target = FixedTarget.from_name(self.celsobj)
        
        with open('dataset.txt', 'a') as f:
            f.write(f"                       {target.ra.degree}")
        return target.coord

    @property
    def target_up_at_midnight(self):
        coords = SkyCoord(self.coord1,self.coord2, frame = 'icrs')
        object = FixedTarget(name = self.celsobj, coord = coords)
        midnight_ioMIT = observatory.midnight(now, which="nearest")
        obs = observatory.target_is_up(midnight_ioMIT,object)
      
        return obs 
    
    @property
    def airmass (self):
        coords = SkyCoord(self.coord1,self.coord2, frame = 'icrs')
        object = FixedTarget(name = self.celsobj, coord = coords)
        target_altaz = observatory.altaz(midnight(observatory), object)
        
        return target_altaz.secz


if path.exists("dataset.txt"):
    celes_object = input("Enter the name of the target : ")
    target = FixedTarget.from_name(celes_object)
    RA = target.ra
    DEC = target.dec
    intel = InformationObjects(RA,DEC,celes_object)
    with open('dataset.txt', 'a') as f:
        f.write(f'\n{celes_object}')
    print(intel.rise_times)
    print(intel.ra_dec)

else:
    with open('dataset.txt', 'a') as f:
        f.write(f"Name                      Rise Time                                    RA")
        print("DataSet Document Created....")
        print("Run the Program Again")


 

     
