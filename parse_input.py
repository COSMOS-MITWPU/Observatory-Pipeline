# File to parse the input file and return the data as python objects

import json
import os
from astropy.coordinates import EarthLocation
from astroplan import Observer
import astropy.units as units

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
    print(ioMIT)
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


def targets_setup():
    # return a list of Objects of the target class pre initialized.
    pass


def constraints_setup():
    file_path = os.path.abspath(file_path)
    constraints_data = open(file_path)

    try:
        data = json.load(constraints_data)
    except FileNotFoundError as err:
        print("CONSTRAINTS JSON FILE NOT FOUND")
        print("The File you provided doesnt exist. Please Check and Enter again")

    return data

date_and_time_path = "./inputs/date_and_time.json" 
date_and_time_setup(date_and_time_path)