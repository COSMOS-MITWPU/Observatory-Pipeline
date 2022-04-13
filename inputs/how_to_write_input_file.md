Here is an example Input file with comments, explaining how the input file must be writte.
1. All numbers must be integers
2. All strings, names and targets must be enclosed in Double Quotes
3. Do not add or remove any Commas, if you do, make sure they arent trailing, and in the right place. 
4. Do not add or remove any Curly Braces, if you do make sure you close them respectively
5. Do not change any of the content in the "observatory" section. 
6. Feel free to add any targets of your choice in the night sky. 
7. Feel free to add any number of targets.

``` json
{
"constraints" : { 
        "airmass": 3,
        "minimum_altitude": 15,
        "maximum_altitude": 85,
        "moon_separation": 10,

        "define_start_time":false,
        "start_time":
                    {
                        "day":20,
                        "month":3,
                        "year": 2022,
                        "hours":20,
                        "minutes":30,
                        "seconds":29
                    },
        "define_end_time":false,
        "end_time":
                    {
                        "day":20,
                        "month":3,
                        "year": 2022,
                        "hours":20,
                        "minutes":30,
                        "seconds":29
                    }
},

"date_and_time":{
        "use_current_time":true,
        "day":20,
        "month":3,
        "year": 2022,
        "hours":20,
        "minutes":30,
        "seconds":29
},

"observatory":{
        "name":"MIT-Telescope",
        "description": "GSO-Newtonian Telescope MIT World Peace University",
        "latitude": 18.51773,
        "longitude":73.81488,
        "elevation":560,
        "timezone":"Asia/Kolkata"
},

"targets":{
    "targets": ["vega", 
                "m31",
                "jupiter",
                "m1",
                "m42",
                "m55",
                "saturn",
                "sun",
                "neptune",
                "moon",
                "venus",
                "mars",
                "orion",
                "betelgeuse",
                "rigel"
            ]
}
}
```