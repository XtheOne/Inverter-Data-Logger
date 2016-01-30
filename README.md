# Omnik Data Logger
=====
Omnik Data Logger is a small script for uploading data from a Omniksol Solar 
inverter or Hosola inverter, equipped with a wifi module from iGEN tech (solarmanpv.com), 
to a database and/or to PVoutput.org. 

This script is designed to be run as a cronjob every minute. Every time this
script is run the data from the inverter will be send to the database. And with
a five minute interval the data will also be uploaded to PVoutput.org as a live
status.
To enable Domoticz support, enable the DomoticzOutput plugin in the config file, and make sensors on dummy hardware and fill the idx of these sensors in the config file.

## Supported inverters
Users reported that this script works for wifi kits with a s/n starting with
602xxxxxx to 606xxxxxx. Also tested with a Wifi kit in a Hosola inverter in the 611xxxxx range.
With wifi kits in the range 601xxxxxx it is not
possible to get the data directly from the inverter. So sniffing the data send
to the omnik portal is required, see OmnikMQTT by wouterbaake
(https://github.com/wouterbaake/OmnikMQTT) .

Owners of a Wifi kit starting with s/n 402xxxxxxx should checkout
Omnikol-PV-Logger by t3kpunk (https://github.com/t3kpunk/Omniksol-PV-Logger).

## Installation and Setup

* Install Python
* Git clone the source with `git clone https://github.com/Woutrrr/Omnik-Data-Logger.git`
* Copy the config-org.cfg to config.cfg
* Change the settings in config.cfg
* Test your settings with `python LiveStats.py`, when successful you should see
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

## Development
To help with development when no sun is present a small simulator script can be
found in the folder Development. This script works by reading values from to
database used by de MysqlOutput, but with the time shifted 6 hours back. To use
the simulator, you should use the MysqlOutput to fill the database and configure
database settings in de sim-config.cfg file.
