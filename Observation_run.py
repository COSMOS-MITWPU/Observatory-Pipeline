# File to produce an output Excel sheet with Observation information of the given targets.

# The way this is going to work is that the user that wants to conduct observations, needs
# to write all the pre requisite information like the observatory location, targets, constraints etc in
# the inputs files given in the ./inputs folder json files. The parse_input files then parses it.
# this file will take functions from parse_input and use its outputs here. 
 
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
from astroplan import moon_illumination# made 0 duo to an error
import parse_input as pi
import os

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

def if_observable(observer, target, constraints):
    """
    Arguements: 
    
    observer: object of the Observer class
    target: object of the Target class
    constraints: dictionary with constraint values
    
    returns: 
    
    whether of not a given target is observable by the Observer 
    with the provided constraints.
    """
    
    
    constraints_list = [AltitudeConstraint(constraints['minimum_altitude']*u.deg, constraints['maximum_altitude']*u.deg),
                    AirmassConstraint(constraints['airmass']),
                    AtNightConstraint.twilight_civil(), 
                    MoonSeparationConstraint(min = constraints['moon_separation'] * u.deg)
               ]
    
    t_range = Time([constraints['start_time'] - 0.5 * u.hour, constraints['end_time'] + 0.5 * u.hour])
    ever_observable = is_observable(constraints_list, observer, target, time_range=t_range)
    return ever_observable

def transit(observer, target):
    """
    Arguements: 
    
    observer: object of the Observer class
    target: object of the Target class
    
    
    Returns:
    
    the transit time in Astropy Units of hours.
    # or a datetime.TimeDelta() object preferably. 
    """
    
    return (rise_time(observer, target) - set_time(observer, target)).to(u.hr)
    # or
    # rise_time = observer.target_rise_time(obs_time, targets[-1], which = 'nearest', horizon=0*u.deg)
    # set_time = observer.target_set_time(obs_time, targets[-1], which = 'next', horizon=0*u.deg)
    # transit_time = observer.astropy_time_to_datetime(rise_time) - observer.astropy_time_to_datetime(set_time)

# only examples
target_names=['vega','polaris','m1','m42','m55']


def main():
    
    # Remove this section entirely, and change it with function calls from the parse_input.py file
    
    ### INPUT BASIC INFO ### 
    
    print("What is the Date and time that you would like to make observations on? (Enter 0 for now, or enter full date)")
    # pi.date_and_time_setup()

    obs_time = input()
    if obs_time == '0':
        obs_time = Time.now()
    else: 
        obs_time = Time(obs_time)
        
        
    # Defining our observer using the function from parse_input file
    # other inputs also to be done like this, and therefore shift some above defined functions to 
    # the parse_input file. Thereby eliminating all required TUI from the user side.
    
    observer = pi.observatory_setup("./inputs/observatory.json")
    
    # defining key times

    sunset_ioMIT = observer.sun_set_time(obs_time, which="nearest")
    eve_twil_ioMIT = observer.twilight_evening_astronomical(obs_time, which="nearest")
    midnight_ioMIT = observer.midnight(obs_time, which="nearest")
    morn_twil_ioMIT = observer.twilight_morning_astronomical(obs_time, which="nearest")
    sunrise_ioMIT = observer.sun_rise_time(obs_time, which="next")

    # Adding rows to the Output info file database
    observer_info = pd.DataFrame(columns = ['Name', 'Date and Time'])
    observer_info.loc[0] = ['Nearest Sunset Time', sunset_ioMIT.iso]
    observer_info.loc[1] = ['Nearest Evening Twilight Time', eve_twil_ioMIT.iso]
    observer_info.loc[2] = ['Nearest Midnight Time', midnight_ioMIT.iso]
    observer_info.loc[3] = ['Nearest Morning Twilight Time', morn_twil_ioMIT.iso]
    observer_info.loc[4] = ['Next Sunrise Time', sunrise_ioMIT.iso]

    observer_info.to_csv(os.path.join(os.getcwd(), 'outputs/Observer_info.csv'))

    ### INPUT CONSTRAINTS ###

    print("\nEnter the Maximum AirMass: ")
    airmass = int(input())
    
    print("Enter the minimum Altitude in degrees (15 default): ")
    min_alt = int(input())

    print("Enter the maximum Altitude in degrees (85 Default): ")
    max_alt = int(input())

    print("Enter Moon Separation (10 is default): ")
    moon_separation = int(input())
    
    print("Enter the Observation start time (0 for evening twilight as default): ")
    start_time = int(input())
    if start_time == 0:
        start_time = eve_twil_ioMIT
    else: start_time = Time(start_time)
    
    print("Enter the observation end time (0 for morning twilight as default): ")
    end_time = int(input())
    
    if end_time == 0:
        end_time = morn_twil_ioMIT
    else: end_time = Time(end_time)
    
    constraints = {
        "airmass": airmass,
        "minimum_altitude": min_alt,
        "maximum_altitude": max_alt,
        "moon_separation": moon_separation,
        "start_time": start_time,
        "end_time": end_time
    }
    
    

    target_info_df = pi.targets_setup("./inputs/targets.json")
        
    # os.path is being used so as to maintain consistancy between OSX and Windows devices. 
    target_info_df.to_csv(os.path.join(os.getcwd(), 'outputs/targets_info.csv'))
    print("file saved. ")

main()
