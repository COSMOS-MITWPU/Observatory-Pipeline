# File to produce an output Excel sheet with Observation information of the given targets.

# Important Libraries. 

import numpy as np
import pytz
import matplotlib.pyplot as plt
import astropy.units as u
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astroplan import Observer, FixedTarget
from astropy.utils.iers import conf
from astroplan import download_IERS_A
from astropy.coordinates import get_sun, get_moon, get_body
from astroplan import moon_illumination
from astroplan.plots import plot_finder_image
from astroquery.skyview import SkyView
from astroplan.plots import plot_sky, plot_airmass
from astropy.table import QTable
from astropy.io import ascii
from astropy.table import Table
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint, MoonSeparationConstraint)
from astroplan import is_observable, is_always_observable, months_observable



conf.auto_max_age = None

# using UTI1
download_IERS_A()

now = Time.now()


def time_in_india():
    """
    Arguements: None
    Returns: The time in India Now
    """
    date = now + 5 * u.h + 30 * u.min
    return date

def observatory_setup(longitude, latitude, elevation, timezone, name, description):
    """
    Returns an Observer Object with location of our Observatory
    """
    location = EarthLocation(longitude, latitude, elevation)
    
    ioMIT = Observer(
        location=location,
        timezone=timezone,
        name=name,
        description=description,
    )
    return ioMIT

def target_is_up(observer, target, time_of_observation):
    is_up = observer.target_is_up(time_of_observation, target)
    return is_up


def target_fix_icrs(longitude, latitude):  # International Celestial Reference System
    coords = SkyCoord(longitude, latitude, frame="icrs")
    return coords


def altitude(observer, time_of_observation, target):
    alt = observer.altaz(time_of_observation, target)
    return alt.alt.degree


def azimuth(observer, time_of_observation, target):
    az = observer.altaz(time_of_observation, target)
    return az.az.degree


def moon():
    return get_moon(now)


def moon_illumination_today():
    return moon_illumination(now)


def airmass(observer, time_of_observation, target):
    target_altaz = observer.altaz(time_of_observation, target)
    return target_altaz.secz


def observation_time_set(start, end, observer):
    observation_time = start + (end - start) * np.linspace(0.0, 1.0, 20)
    return observation_time


def x_degree_horizon(observer, target, degree):
    time = observer.target_rise_time(
        now, target, which="next", horizon=degree * u.deg
    ).iso
    return time


def rise_time(observer,target):
    time=observer.target_rise_time(now,target).iso
    return time


def set_time(observer,target):
    time=observer.target_set_time(now,target).iso
    return time

def if_observable(observer, target, t_start, t_end):
    constraints = [AltitudeConstraint(15*u.deg, 84*u.deg),
               AirmassConstraint(3), AtNightConstraint.twilight_civil(), MoonSeparationConstraint(min = 10 * u.deg)]
    t_range = Time([t_start - 0.5 * u.hour, t_end + 0.5 * u.hour])
    ever_observable = is_observable(constraints, observer, target, time_range=t_range)
    return ever_observable
    
def transit(observer, target):
    return (rise_time(observer, target) - set_time(observer, target)).to(u.hr)
    # or
    # rise_time = observer.target_rise_time(obs_time, targets[-1], which = 'nearest', horizon=0*u.deg)
    # set_time = observer.target_set_time(obs_time, targets[-1], which = 'next', horizon=0*u.deg)
    # transit_time = observer.astropy_time_to_datetime(rise_time) - observer.astropy_time_to_datetime(set_time)

target_names=['vega','polaris','m1','m42','m55']


def main():
    print("What is the Date and time that you would like to make observations on? (Enter 0 for now, or enter full date)")

    obs_time = input()
    if obs_time == '0':
        obs_time = Time.now()
    else: 
        obs_time = Time(obs_time)
        
    print("Enter the location of the observatory (0 for MIT Observatory, LAT and LON for Others)")

    observer = input()
    if observer == '0': # make observer as our observatory
        observer = observatory_setup("73d48m53s", 
                                        "18d31m7s",
                                        560 * u.m, 
                                        "Asia/Kolkata", 
                                        "MIT-Telescope",
                                        "GSO-Newtonian Telescope MIT World Peace University")
    else: 
        print("enter the details for the other location")
        
    # defining key times

    sunset_ioMIT = observer.sun_set_time(now, which="nearest")
    eve_twil_ioMIT = observer.twilight_evening_astronomical(now, which="nearest")
    midnight_ioMIT = observer.midnight(now, which="nearest")
    morn_twil_ioMIT = observer.twilight_morning_astronomical(now, which="nearest")
    sunrise_ioMIT = observer.sun_rise_time(now, which="next")

    # Printing Key times, as they help us make decisions for targets later on. Therefore seems information worth 
    # printing to the user.

    print("Sunset at MIT Observatory will be at {0.iso} UTC".format(sunset_ioMIT))
    print("Astronomical evening twilight at MIT Observatory will be at {0.iso} UTC".format(eve_twil_ioMIT))
    print("Midnight at MIT Observatory will be at {0.iso} UTC".format(midnight_ioMIT))
    print("Astronomical morning twilight at MIT Observatory will be at {0.iso} UTC".format(morn_twil_ioMIT))
    print("Sunrise at MIT Observatory will be at {0.iso} UTC".format(sunrise_ioMIT))

    print("Enter target Name(s): (Enter 0 when done)")

    targets = [] # Empty list to hold Target objects of the target class

    target = input()

    target_info_df = pd.DataFrame(columns = ['TARGET','RA','DEC','RISE TIME','SET TIME', 'TRANSIT', 'OBSERVABLE DURING TRANSIT?'])

    database_index = 0
    while(target != "0"):
        try:
            targets.append(FixedTarget.from_name(target))       
            rise_time = observer.target_rise_time(obs_time, targets[-1], which = 'nearest', horizon=0*u.deg)
            set_time = observer.target_set_time(obs_time, targets[-1], which = 'next', horizon=0*u.deg)
            transit_time = observer.astropy_time_to_datetime(rise_time) - observer.astropy_time_to_datetime(set_time)
            observable = if_observable(observer, targets[-1], eve_twil_ioMIT, morn_twil_ioMIT)
            
            
            # Adding a row to the database. 
            target_info_df.loc[database_index] = [target, # Name
                                        targets[-1].ra.degree, # RA 
                                        targets[-1].dec.degree,  # DEC
                                        rise_time.iso, # Rise time
                                        set_time.iso, # Set time
                                        transit_time, # Transit
                                        observable # Whether or not the object is observable
                                        ]
            database_index += 1
            
        except: 
            print("the target you entered is not in the database. Please Enter again.")
        target = input()
        
    target_info_df.to_csv("values.csv")
    print("file saved. ")    
    
    
main()