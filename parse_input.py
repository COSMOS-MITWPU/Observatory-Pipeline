# File to parse the input file and return the data as python objects

import json
import os
from astropy.coordinates import EarthLocation
from astroplan import Observer, FixedTarget
import astropy.units as units
import pandas as pd

# Opening JSON file
# file_path=open("./inputs/observatory.json")


def observatory_setup(file_path):
    """
    Parse input observatory.json file

    Inputs:
        Absolute or relative path of the input json file containing
        information about the observatory
    Returns:
        an object of the Observer class from Astroplan
    """

    # Getting the absolute path to avoid confusion
    file_path = os.path.abspath(file_path)
    observator_data = open(file_path)

    # Parsing the file
    try:
        data = json.load(observator_data)
    except FileNotFoundError as err:
        print("OBSERVATORY JSON FILE NOT FOUND")
        print("The File you provided doesnt exist. Please Check and Enter again")

    # Calculating and Returning the object.

    location = EarthLocation(
        data["longitude"], data["latitude"], data["elevation"] * units.m
    )

    ioMIT = Observer(
        location=location,
        timezone=data["timezone"],
        name=data["name"],
        description=data["description"],
    )
    return ioMIT


def date_and_time_setup(file_path):
    # return a list of the important dates and times like day and time of observation
    # or return a single astropy date object without formatitng.
    # or return a datetime_object
    file = json.load(open(file_path))

    day = file["day"]
    month = file["month"]
    year = file["year"]
    hours = file["hours"]
    minutes = file["minutes"]
    seconds = file["seconds"]

    return_array = [day, month, year, hours, minutes, seconds]
    # print(return_array)
    return (return_array)
    pass

def targets_setup(file_path):
    # return a list of Objects of the target class pre initialized.
    

    file_path = os.path.abspath(file_path)
    targets_data = open(file_path)
    
    
    # Parsing the file
    try:
        targets_data = json.load(targets_data)
    except FileNotFoundError as err:
        print("TARGETS JSON FILE NOT FOUND")
        print("The File you provided doesnt exist. Please Check and Enter again")

    targets_list = targets_data['targets']
    database_index = 0

    # Defining the DataBase
    target_info_df = pd.DataFrame(columns = ['TARGET','RA','DEC','RISE TIME','SET TIME', 'TRANSIT', 'OBSERVABLE DURING TRANSIT?'])

    for target in targets_list:
        targets.append(FixedTarget.from_name(target))       
        rise_time = observer.target_rise_time(obs_time, targets[-1], which = 'nearest', horizon=0*u.deg)
        set_time = observer.target_set_time(obs_time, targets[-1], which = 'next', horizon=0*u.deg)
        transit_time = 0 # made 0 duo to an error
        # observer.astropy_time_to_datetime(rise_time) - observer.astropy_time_to_datetime(set_time)
        observable = 0 # made 0 duo to an error
        # if_observable(observer, targets[-1], eve_twil_ioMIT, morn_twil_ioMIT)
        
        
        # Adding a row to the database with calculated values. 
        target_info_df.loc[database_index] = [target, # Name
                                    targets[-1].ra.degree, # RA 
                                    targets[-1].dec.degree,  # DEC
                                    rise_time.iso, # Rise time
                                    set_time.iso, # Set time
                                    transit_time, # Transit
                                    observable # Whether or not the object is observable
                                    ]
    # os.path is being used so as to maintain consistancy between OSX and Windows devices. 
    target_info_df.to_csv(os.path.join(os.getcwd(), 'outputs/targets_info.csv'))
    print("file saved. ")


def constraints_setup():
    file_path = os.path.abspath(file_path)
    constraints_data = open(file_path)

    try:
        data = json.load(constraints_data)
    except FileNotFoundError as err:
        print("CONSTRAINTS JSON FILE NOT FOUND")
        print("The File you provided doesnt exist. Please Check and Enter again")

    return data
    
    
    pass

    return data

date_and_time_path = "./inputs/date_and_time.json" 
date_and_time_setup(date_and_time_path)