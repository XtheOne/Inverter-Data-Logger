# Omnik Data Logger
=====
Omnik Data Logger is a small script for uploading data from a Omniksol Solar 
inverter, equipped with a wifi module, to a database and/or to PVoutput.org. 
For now only wifi kits with a s/n starting with 602 are supported

This script is designed to be run as a cronjob every minute. Every time this 
script is run the data from the inverter will be send to the database. And with 
a five minute interval the data will also be uploaded to PVoutput.org as a live 
status.

## Installation and Setup

* Install Python
* Git clone the source with `git clone https://github.com/Woutrrr/Omnik-Data-Logger.git`
* Copy the config-org.cfg to config.cfg
* Change the settings in config.cfg
* Test your settings with `python LiveStats.py`, when succesfull you should see 
data from your inverter
* Run the script with `python OmnikExport.py` or better set a scheduled task or 
cronjob.

### Example cronjob
With these options this will execute the script every minute.

`* * * * * /usr/bin/python /home/username/Omnik-Data-Logger/OmnikExport.py`

### Why copy config-org.cfg, can't I edit it directly?
Yes you can edit config-org.cfg directly. However if you want to update the 
script your settings will be overwritten with the default values. By creating 
config.cfg, you can preserve your settings when upgrading.

## TODO
* Decode more data from the inverter response
* Error handling
* Modular upload system (ie. create a system for easy adding additional uploader like mysql, pvoutput)


