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
import matplotlib.pyplot as plt
from astroplan.plots import plot_sky, plot_airmass
from astropy.table import QTable
from astropy.io import ascii
from astropy.table import Table
import astropy.units as u
import numpy as np
import pandas as pd

download_IERS_A()
now = Time.now()


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


def sunset(observatory=observatory_setup()):
    sunset_ioMIT = observatory.sun_set_time(now, which="nearest")
    return sunset_ioMIT


def evening_twilight(observatory=observatory_setup()):
    eve_twil_ioMIT = observatory.twilight_evening_astronomical(now, which="nearest")
    return eve_twil_ioMIT


def midnight(observatory=observatory_setup()):
    midnight_ioMIT = observatory.midnight(now, which="nearest")
    return midnight_ioMIT


def morn_twilight(observatory=observatory_setup()):
    morn_twil_ioMIT = observatory.twilight_morning_astronomical(now, which="nearest")
    return morn_twil_ioMIT


def sunrise(observatory=observatory_setup()):
    sunrise_ioMIT = observatory.sun_rise_time(now, which="next")
    return sunrise_ioMIT


def local_siderial_time(observatory=observatory_setup()):
    lst = observatory.local_siderial_time(now)
    return lst


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


# print(airmass(observatory_setup(),evening_twilight(observatory_setup()),target=FixedTarget.from_name('m51')))


def plot_target(target, observer, time_of_observation):
    plot_sky(target, observer, time_of_observation)
    plt.show()


# plot_target(FixedTarget.from_name('m51'),observatory_setup(),evening_twilight(observatory_setup()))


def observation_time_set(start, end, observer):
    observation_time = start + (end - start) * np.linspace(0.0, 1.0, 20)
    return observation_time


# print(observation_time_set(evening_twilight(observatory_setup()),evening_twilight(observatory_setup()),observatory_setup()))


def plot_imager(target):
    plot_finder_image(target, fov_radius=20 * u.arcmin)
    plt.show()


# plot_imager(FixedTarget.from_name('m51'))


def airmass_plot(target, observer, observation_time):
    plot_airmass(target, observer, observation_time)
    plt.ylim(4, 0.5)
    plt.show()


# airmass_plot(
#     target=FixedTarget.from_name("m51"),
#     observer=observatory_setup(),
#     observation_time=observation_time_set(
#         evening_twilight(observatory_setup()),
#         morn_twilight(observatory_setup()),
#         observatory_setup(),
#     ),
# )


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

# print(x_degree_horizon(observatory_setup(),FixedTarget.from_name('m51'),30))

cel_body=input("Enter the Celestial Body:")


target_names=['vega','polaris','m1','m42','m55']
target_names.append(cel_body)
targets=[FixedTarget.from_name(x) for x in target_names]

ra=[]
dec=[]
rise_times=[]
set_times=[]
visibility=[]
for target in targets:
    ra.append(target.ra.degree)
    dec.append(target.dec.degree)
    
for i in targets:
    rise_times.append(rise_time(observatory_setup(),i))

for i in targets:
    set_times.append(set_time(observatory_setup(),i))

for i in targets:
    visibility.append(target_is_up(observatory_setup(),i,midnight()))

names=np.array(target_names)
a=np.array(ra)
b=np.array(dec)
c=np.array(rise_times)
d=np.array(set_times)

t=QTable([names,a,b,c,d],names=('TARGET','RA','DEC','RISE TIME','SET TIME'))

df=pd.DataFrame([names,a,b,c,d],index=['TARGET','RA','DEC','RISE TIME','SET TIME'])

df.to_excel("values.xlsx")

t.pprint()
print(visibility)

# print(rise_time(observatory_setup(),FixedTarget.from_name('m55')))
