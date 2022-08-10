# Aaryabhatta Observatory

##### We are COSMOS, a student astronomy club based out of MIT-WPU with projects ranging from an Observatory for optical astronomy to a ground station for radio astronomy.


# Observatory Project
## Our Equipment
1) Telescopes
	- GSO 10-inch RC
	- 8-inch Newtonian 
2) Mount
	- Sky watcher EQ6R Pro Go-To
3) Cameras
	- ZWO 1600mm pro monochrome
	- ASI462MC (Color)

## Python Pipline
1) **Observation Run Preparation** <br/>
	When scheduling an observation session , it is of paramount importance to keep track of the objects of interest for the said observation and the availabilty of those celestial objects . An Observation Run Preparation software plays the part of conveying when the objects are visible and if they meet the standards needed to extract scientific data out of them


	Requirements :
	1) [Numpy](https://numpy.org/)
	2) [Astropy](https://docs.astropy.org/en/stable/index.html)
	3) [Astroplan](https://astroplan.readthedocs.io/en/latest/)
	4) [Pandas](https://pandas.pydata.org/)

	[observation_run.py ](https://github.com/COSMOS-MITWPU/Observatory-Documentation/blob/main/observation_run/Observation_run.py)
		The aim of this file is to produce an output Excel sheet with Observation information of the given astronomical targets. The user needs to write all the pre-requisite information like the observatory location, targets, constraints etc in the inputs files given in the [./inputs](https://github.com/COSMOS-MITWPU/Observatory-Documentation/tree/main/inputs) folder json files. The method of writing the inputs is given in [this](https://github.com/COSMOS-MITWPU/Observatory-Documentation/blob/main/inputs/how_to_write_input_file.md) file. The [parse_input](https://github.com/COSMOS-MITWPU/Observatory-Documentation/blob/main/observation_run/parse_input.py) file then parses it and routes it to the [main](https://github.com/COSMOS-MITWPU/Observatory-Documentation/blob/main/observation_run/Observation_run.py) program.
