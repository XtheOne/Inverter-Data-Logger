# Inverter Data Logger
Inverter Data Logger is a small script for uploading data from a 
Omnik, Hosola, Goodwe, Solax, Ginlong, Samil, Sofar or Power-One
Solar inverter, equipped with a wifi module or connected to a Wi-Fi data logger
from [iGEN tech](http://solarmanpv.com/index_en.html), to a database, [Domoticz](http://domoticz.com/) 
and/or to [PVoutput.org](https://pvoutput.org/).

This script is designed to be run as a cronjob (or scheduled tasks on Windows) every minute.
Every time this script is run the data from the inverter(s) will be send to the enabled plugin(s).
And with a five minute interval the data will also be uploaded to PVoutput.org as a live status when enabled.

## Origin
This is based on the original work of Wouter van der Zwan and includes some improvements made by others.

## Supported inverters
- Users reported that this script works for wifi kits with a s/n starting with 602xxxxxx to 606xxxxxx.
- Also tested with a Wifi kit in a Hosola inverter in the 611xxxxx range.
- Also works for newer 1601xxxxxx WiFi kit as used in the Omnik TL2 inverters.
- Also works with iGEN Wi-Fi external loggers with s/n starting with 504xxxxxx

With wifi kits in the range 601xxxxxx it is **not** possible to get the data directly from the 
inverter. So sniffing the data send to the Omnik portal is required, see [OmnikMQTT by 
wouterbaake](https://github.com/wouterbaake/OmnikMQTT) .

Owners of a Wifi kit starting with s/n 402xxxxxxx should checkout
[Omnikol-PV-Logger by t3kpunk](https://github.com/t3kpunk/Omniksol-PV-Logger).

## Installation and Setup
* Install Python (tested with python-2.7.14 and python-3.6.4)
* Git clone the source with `git clone https://github.com/XtheOne/Inverter-Data-Logger.git`
* Copy the `config-org.cfg` to `config.cfg`
* Change the settings in `config.cfg` (See '[Configuration](#configuration)')
* Test your settings with `python LiveStats.py`, when successful you should see data from your inverter. (you have to install several modules...)
* Run the script with `python InverterExport.py` or better set a scheduled task or cronjob. (See '[Setting cronjob](#setting-cronjob)')

## Configuration
To enable Domoticz support, enable the DomoticzOutput plugin in the config file.
Then Create the following new hardware:
* Name: Inverter Virtual
* Type: Dummy (Does nothing, use for virtual switches only)
* Data Timeout: Disabled

Now Create the following Virtual Sensors:

| Identifier               | Sensor Type                  | Name                    |
| ------------------------ | ---------------------------- | ----------------------  |
| Electric_meter_idx       | Electric (Instant + Counter) | Actual Output Power (after creation, set 'Type:' to 'Return' and 'Energy read:' to 'From device') |
| PV1_voltage_idx          | Voltage                      | DC Voltage PV1          |
| PV2_voltage_idx          | Voltage                      | DC Voltage PV2          |
| PV1_current_idx          | Ampere (1 Phase)             | DC Current PV1          |
| PV2_current_idx          | Ampere (1 Phase)             | DC Current PV2          |
| AC1_voltage_idx          | Voltage                      | AC Output Voltage       |
| AC1_current_idx          | Ampere (1 Phase)             | AC Output Current       |
| AC1_power_idx            | Usage (Electric)             | AC Output Power         |
| AC1_frequency_idx        | Custom Sensor (Hertz)        | AC Frequency            |
| --- Optional sensors --- |                              |                         |
| Temp_idx                 | Temperature                  | Temperature             |
| H_total_idx              | Custom Sensor (Hours)        | Total run Hours         |
| PV123_voltage_idx        | Ampere (3 Phase)             | DC Voltage PV1/2/3 (No 3 phase voltage device exists...) |
| PV123_current_idx        | Ampere (3 Phase)             | DC Current PV1/2/3      |
| AC123_voltage_idx        | Ampere (3 Phase)             | AC 1/2/3 Output Voltage (No 3 phase voltage device exists...) |
| AC123_current_idx        | Ampere (3 Phase)             | AC 1/2/3 Output Current |
| AC123_power_idx          | Usage (Electric)             | AC Output Power (total for 3 phase inverter) |
| E_today_idx              | Custom Sensor (kWh)          | Energy today            |
| E_total_idx              | Custom Sensor (kWh)          | Total Energy            |
| E_total_c_idx            | Counter                      | Energy production (after creation, set Type to 'Energy Generated') |

Now go to Devices and fill the Idx of these virtual sensors into the config file.
This is for a single phase inverter with 2 PV strings and basic values, more virtual sensors can be added for other identifiers.

### Setting cronjob
#### For Linux/Unix
This crontab line with these options this will execute the script every minute.
* crontab -e
* Add row: `* * * * * /usr/bin/python /home/username/Inverter-Data-Logger/InverterExport.py`

#### For Windows
This scheduled task with these options this will execute the script every minute.
* Start (or My Computer) -> Control Panel -> Scheduled Tasks -> Add Scheduled Task ->  
or
* Start -> All Programs -> Administrative Tools -> Task Scheduler -> Action -> New Task ->
    * General (tab) ->
       * Name: InverterExport
       * Description: Attempt to fire up the solar inverter exporter.
       * Select 'Run whether user is logged on or not' and 'Do not store password.'
       * Select 'Run with highest privileges.'
    * Triggers (tab) -> New ->
       * Begin the task: 'On a schedule'
       * Settings: 'Daily' '00:00:00 AM'. Recur every: 1 days.
       * Repeat task every: '1 minutes' for a duration of: '1 day' (or 'Indefinitely')
       * 'Enabled'
       * -> OK.
    * Actions (tab) -> New ->
       * Action: 'Start a program'
       * Program/script: C:\Inverter-Data-Logger\InverterExport.py
       * -> OK.
    * Conditions (tab) ->
       * choose your own options.
    * Settings (tab) ->
       * 'Allow task to be run on demand'
       * 'Stop the task if it runs longer than: '2 days'
       * If the task is already running, then the following rule applies: 'Do not start a new instance'
       * -> OK  

NOTE: If you need to kill the process manually: open Task Manager > Processes > Tick 'Show Processes from all users' > right click 'python.exe' > select 'End Process'.

### Why copy config-org.cfg, can't I edit it directly?
Yes you can edit `config-org.cfg` directly. However, if you want to update the 
script your settings will be overwritten with the default values. By creating 
`config.cfg`, you can preserve your settings when upgrading.

## Development
To help with development when no sun is present a small simulator script can be
found in the folder Development. This script works by reading values from to
database used by the MysqlOutput, but with the time shifted 6 hours back. To use
the simulator, you should use the MysqlOutput to fill the database and configure
database settings in de `sim-config.cfg` file.
