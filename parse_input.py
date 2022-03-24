# File to parse the input file and return the data as python objects

import json
import os
from astropy.coordinates import EarthLocation
from astroplan import Observer, FixedTarget
from astropy.time import Time
import astropy.units as units
import pandas as pd
from datetime import datetime
from astroplan import (
    AltitudeConstraint,
    AirmassConstraint,
    AtNightConstraint,
    MoonSeparationConstraint,
)
from astroplan import is_observable, is_always_observable, months_observable
from astropy.coordinates import solar_system_ephemeris, EarthLocation
from astropy.coordinates import get_body_barycentric, get_body, get_moon


def if_observable(observer, target, constraints):
    """
    Arguments:

    observer: object of the Observer class
    target: object of the Target class
    constraints: dictionary with constraint values

    returns:

    whether of not a given target is observable by the Observer
    with the provided constraints.
    """

    constraints_list = [
        AltitudeConstraint(
            constraints["minimum_altitude"] * units.deg,
            constraints["maximum_altitude"] * units.deg,
        ),
        AirmassConstraint(constraints["airmass"]),
        AtNightConstraint.twilight_civil(),
        MoonSeparationConstraint(min=constraints["moon_separation"] * units.deg),
    ]

    t_range = Time(
        [
            constraints["start_time"] - 0.5 * units.hour,
            constraints["end_time"] + 0.5 * units.hour,
        ]
    )
    ever_observable = is_observable(
        constraints_list, observer, target, time_range=t_range
    )
    return ever_observable[0]  # return the first element of the list


def transit(observer, target):
    """
    Arguments:

    observer: object of the Observer class
    target: object of the Target class


    Returns:

    the transit time in Astropy Units of hours.
    # or a datetime.TimeDelta() object preferably.
    """
    rise_time = observer.target_rise_time(
        obs_time, targets[-1], which="nearest", horizon=0 * u.deg
    )
    set_time = observer.target_set_time(
        obs_time, targets[-1], which="next", horizon=0 * u.deg
    )
    transit_time = set_time - rise_time

    return transit_time.to(units.hr)
    # or


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

    location = EarthLocation.from_geodetic(
        data["longitude"] * units.deg,
        data["latitude"] * units.deg,
        data["elevation"] * units.m,
    )

    ioMIT = Observer(
        location=location,
        timezone=data["timezone"],
        name=data["name"],
        description=data["description"],
    )
    return ioMIT


def json_to_astropy_time(json_dictionary):
    # simply returns the astropy time from a json dictionary
    # this function exists coz this process is done repeatedly in start_time, end_time
    # and observation_time

    python_time = datetime(
        json_dictionary["year"],
        json_dictionary["month"],
        json_dictionary["day"],
        json_dictionary["hours"],
        json_dictionary["minutes"],
        json_dictionary["seconds"],
    )
    # Converting to astropy Time object, as astropy functions are expecting this.
    astropy_time = Time(python_time, format="datetime", scale="utc")
    return astropy_time


def date_and_time_setup(file_path):
    # return an astropy Time object from the input data_time.json file.
    # so that other functions can directly use it.
    date_data = json.load(open(file_path))

    if date_data["use_current_time"] is True:
        return Time.now()

    astropy_time = json_to_astropy_time(date_data)
    return astropy_time


def targets_setup(file_path, observer, constraints, obs_time):
    # returns a pandas dataFrame of the targets reading them from the
    # input targets.json file, and information about them, with relevant constraints
    # defined in the constraints.json file.

    file_path = os.path.abspath(file_path)
    targets_data = open(file_path)

    # Parsing the file
    try:
        targets_data = json.load(targets_data)
    except FileNotFoundError as err:
        print("TARGETS JSON FILE NOT FOUND")
        print("The File you provided doesnt exist. Please Check and Enter again")

    targets_list = targets_data["targets"]

    # Defining the DataBase
    target_info_df = pd.DataFrame(
        columns=[
            "TARGET",
            "RA",
            "DEC",
            "RISE TIME",
            "SET TIME",
            "TRANSIT (Hours)",
            "OBSERVABLE DURING TRANSIT?",
        ]
    )

    for i, target in enumerate(targets_list):

        try:
            initialized_target = FixedTarget.from_name(target)
            rise_time = observer.target_rise_time(
                obs_time, initialized_target, which="nearest", horizon=0 * units.deg
            )
            set_time = observer.target_set_time(
                obs_time, initialized_target, which="next", horizon=0 * units.deg
            )
            transit_time = round((set_time - rise_time).to(units.hr).value, 2)
        except TypeError as err:
            print("There was an error while finding the transit time of", target)
            transit_time = 0
        except:
            print("cant find the target in the database: ", target)
            print("looking for it in the Solar Database")
            try:
                with solar_system_ephemeris.set("builtin"):
                    initialized_target = get_body(target, obs_time, observer.location)
                    rise_time = observer.target_rise_time(
                        obs_time,
                        initialized_target,
                        which="nearest",
                        horizon=0 * units.deg,
                    )
                    set_time = observer.target_set_time(
                        obs_time,
                        initialized_target,
                        which="next",
                        horizon=0 * units.deg,
                    )
                    transit_time = round((set_time - rise_time).to(units.hr).value, 2)
                    print("found in solar database")
            except:
                print("not found in solar database either. Skipping")
                continue
        observable = if_observable(observer, initialized_target, constraints)

        # Adding a row to the database with calculated values.
        target_info_df.loc[i] = [
            target,  # Name
            initialized_target.ra.degree,  # RA
            initialized_target.dec.degree,  # DEC
            rise_time.iso,  # Rise time
            set_time.iso,  # Set time
            transit_time,  # Transit
            observable,  # Whether or not the object is observable
        ]

    return target_info_df


def constraints_setup(file_path):
    # Returns the basic constraints that we need to check if a target is observable or not.
    # as a dictionary from the input constraints.json file.

    file_path = os.path.abspath(file_path)
    constraints_data = open(file_path)

    try:
        data = json.load(constraints_data)
    except FileNotFoundError as err:
        print("CONSTRAINTS JSON FILE NOT FOUND")
        print("The File you provided doesnt exist. Please Check and Enter again")

    # if start time isnt defined, then well use the evening twilight time as default.
    if data["define_start_time"] is False:
        data["start_time"] = json_to_astropy_time(data["start_time"])
    else:
        eve_twil_ioMIT = observer.twilight_evening_astronomical(
            obs_time, which="nearest"
        )
        data["start_time"] = eve_twil_ioMIT

    # if end time isnt defined, then well use the next morning twilight time as default.
    if data["define_end_time"] is False:
        data["end_time"] = json_to_astropy_time(data["end_time"])
    else:
        morn_twil_ioMIT = observer.twilight_morning_astronomical(
            obs_time, which="nearest"
        )
        data["end_time"] = morn_twil_ioMIT

    return data
