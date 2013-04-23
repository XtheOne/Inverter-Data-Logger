# Omnik Data Logger
=====
Omnik Data Logger is a small script for uploading data from a Omniksol Solar inverter, equipped with a wifi module, to a database and/or to PVoutput.org.

This script is designed to be run as a cronjob every minute. Every time this script is run the data from the inverter will be send to the database. And with a five minute interval the data will also be uploaded to PVoutput.org as a live status.

## Installation and Setup

* Install Python
* Git clone the source
* Copy the config_default.py to config.py
* Change the settings in config.py
* Run the script with `python OmnikExport.py` or better set a scheduled task or cronjob.

### Example cronjob
With these options this will execute the script every minute.

`* * * * * /usr/bin/python /home/username/Omnik-Data-Logger/OmnikExport.py`

## TODO
* Decode more data from the inverter response
* Error handling
* Modular upload system (ie. create a system for easy adding additional uploader like mysql, pvoutput)


