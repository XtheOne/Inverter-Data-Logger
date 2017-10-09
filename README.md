<style>h1{margin:0;}h2{margin:0;}h3{margin:0;}h4{margin:0;}</style>
<h1></a>Inverter Data Logger</h1><hr>
<p>Inverter Data Logger is a small script for uploading data from a Omnik, Hosola, Goodwe, Solax, Ginlong, Samil, Sofar or Power-One Solar inverter, equipped with a wifi module or connected to a Wi-Fi data logger from iGEN tech (solarmanpv.com), to a database, Domoticz and/or to PVoutput.org.</p>
<p>This script is designed to be run as a cronjob (or scheduled tasks on Windows) every minute.
<br>Every time this script is run the data from the inverter(s) will be send to the enabled plugin(s).
<br>And with a five minute interval the data will also be uploaded to PVoutput.org as a live status when enabled.</p>

<h2>Origin</h2><hr>
<p>This is based on the original work of Wouter van der Zwan and includes some improvements made by others.</p>

<h2>Supported inverters</h2><hr>
<p>Users reported that this script works for wifi kits with a s/n starting with 602xxxxxx to 606xxxxxx.
<br>Also tested with a Wifi kit in a Hosola inverter in the 611xxxxx range.
<br>Also works for newer 1601xxxxxx WiFi kit as used in the Omnik TL2 inverters.
<br>Also works with iGEN Wi-Fi external loggers with s/n starting with 504xxxxxx
<br>With wifi kits in the range 601xxxxxx it is not possible to get the data directly from the inverter.
<br>So sniffing the data send to the omnik portal is required, see OmnikMQTT by wouterbaake (<a href="https://github.com/wouterbaake/OmnikMQTT">https://github.com/wouterbaake/OmnikMQTT</a>).
<br>Owners of a Wifi kit starting with s/n 402xxxxxxx should checkout Omnikol-PV-Logger by t3kpunk (<a href="https://github.com/t3kpunk/Omniksol-PV-Logger">https://github.com/t3kpunk/Omniksol-PV-Logger</a>).</p>

<h2>Installation and Setup</h2><hr>
<ul>
<li>Install Python</li>
<li>Git clone the source with <code>git clone https://github.com/XtheOne/Inverter-Data-Logger.git</code></li>
<li>Copy the config-org.cfg to config.cfg</li>
<li>Change the settings in config.cfg (See <a href="#configuration">'Configuration'</a>)</li>
<li>Test your settings with <code>python LiveStats.py</code>, when successful you should see data from your inverter</li>
<li>Run the script with <code>python InverterExport.py</code> or better set a scheduled task or cronjob. (See <a href="#cronjob">'Setting cronjob')</a></li>
</ul>

<h2><a name="configuration"></a>Configuration</h2><hr>
<p>To enable Domoticz support, enable the DomoticzOutput plugin in the config file. Then Create the following new hardware:
<li>Name: Inverter Virtual
<li>Type: Dummy (Does nothing, use for virtual switches only)
<li>Data Timeout: Disabled</p>
<h3>Now Create the following Virtual Sensors:</h3>
<table style="width:100%;text-align: left;padding: 10px;">
  <tr>
    <th>Identifier</th>
    <th>Sensor Type</th>
    <th>Name</th>
  </tr>
  <tr>
    <th margin:0;><hr></th>
    <th><hr></th>
    <th><hr></th>
  </tr>
  <tr>
  	<th>Electric_meter_idx</th>
  	<th>Electric (Instant + Counter)</th>
  	<th>Actual Output Power (after creation, set 'Type:' to 'Return' and 'Energy read:' to 'From device')</th>
  </tr>
  <tr>
  	<th>PV1_voltage_idx</th>
  	<th>Voltage</th>
  	<th>DC Voltage PV1</th>
  </tr>
  <tr>
  	<th>PV2_voltage_idx</th>
  	<th>Voltage</th>
  	<th>DC Voltage PV2</th>
  </tr>
  <tr>
  	<th>PV1_current_idx</th>
  	<th>Ampere (1 Phase)</th>
  	<th>DC Current PV1</th>
  </tr>
  <tr>
  	<th>PV2_current_idx</th>
  	<th>Ampere (1 Phase)</th>
  	<th>DC Current PV2</th>
  </tr>
  <tr>
  	<th>AC1_voltage_idx</th>
  	<th>Voltage</th>
  	<th>AC Output Voltage</th>
  </tr>
  <tr>
  	<th>AC1_current_idx</th>
  	<th>Ampere (1 Phase)</th>
  	<th>AC Output Current</th>
  </tr>
  <tr>
  	<th>AC1_power_idx</th>
  	<th>Usage (Electric)</th>
  	<th>AC Output Power</th>
  </tr>
  <tr>
  	<th>AC1_frequency_idx</th>
  	<th> Custom Sensor (Hertz)</th>
  	<th>AC Frequency</th>
  </tr>
  <tr>
  	<th align="center">--- Optional sensors ---</th>
  </tr>
  <tr>
  	<th>Temp_idx</th>
  	<th>Temperature</th>
  	<th>Temperature</th>
  </tr>
  <tr>
  	<th>H_total_idx</th>
  	<th>Custom Sensor (Hours)</th>
  	<th>Total run Hours</th>
  </tr>
  <tr>
  	<th>PV123_voltage_idx</th>
  	<th>Ampere (3 Phase)</th>
  	<th>DC Voltage PV1/2/3 (No 3 phase voltage device exists...)</th>
  </tr>
  <tr>
  	<th>PV123_current_idx</th>
  	<th>Ampere (3 Phase)</th>
  	<th>DC Current PV1/2/3</th>
  </tr>
  <tr>
  	<th>AC123_voltage_idx</th>
  	<th> Ampere (3 Phase)</th>
  	<th>AC 1/2/3 Output Voltage (No 3 phase voltage device exists...)</th>
  </tr>
  <tr>
  	<th>AC123_current_idx</th>
  	<th>Ampere (3 Phase)</th>
  	<th>AC 1/2/3 Output Current</th>
  </tr>
  <tr>
  	<th>AC123_power_idx</th>
  	<th>Usage (Electric)</th>
  	<th>AC Output Power (total for 3 phase inverter)</th>
  </tr>
  <tr>
  	<th>E_today_idx</th>
  	<th>Custom Sensor (kWh)</th>
  	<th>Energy today</th>
  </tr>
  <tr>
  	<th>E_total_idx</th>
  	<th>Custom Sensor (kWh)</th>
  	<th>Total Energy</th>
  </tr>
  <tr>
  	<th>E_total_c_idx</th>
  	<th>Counter</th>
  	<th>Energy production (after creation, set Type to 'Energy Generated')</th>
  </tr>
</table>
<p>Now go to Devices and fill the Idx of these virtual sensors into the config file.
<br>This is for a single phase inverter with 2 PV strings and basic values, more virtual sensors can be added for other identifiers.</p>

<h2><a name="cronjob"></a>Setting cronjob</h2><hr>
<p><h4>For Linux/Unix</h4>
This crontab line with these options this will execute the script every minute.
<li>crontab -e</li>
<li>Add row: * * * * * /usr/bin/python /home/username/Inverter-Data-Logger/InverterExport.py</li></p>
<p><h4>For Windows</h4>
<li>Start (or My Computer) -&gt; Control Panel -&gt; Scheduled Tasks -&gt; Add Scheduled Task -&gt;</li>
or
<li>Start -&gt; All Programs -&gt; Administrative Tools -&gt; Task Scheduler -&gt; Action -&gt; Create Task -&gt;</li>
<ul>General (tab) -&gt;
<ul><li>Name: InverterExport</li>
<li>Description: Attempt to fire up the solar inverter exporter.</li>
<li>Select 'Run whether user is logged on or not' and 'Do not store password.'</li>
<li>Select 'Run with highest privileges.'</li></ul>
Triggers (tab) -&gt; New -&gt;
<ul><li>Begin the task: 'On a schedule'</li>
<li>Settings: 'Daily' '00:00:00 AM'. Recur every: 1 days.</li>
<li>Repeat task every: '1 minutes' for a duration of: '1 day' (or 'Indefinitely')</li>
<li>'Enabled'</li>
<li>-&gt; OK.</li></ul>
Actions (tab) -&gt; New -&gt;
<ul><li>Action: 'Start a program'</li>
<li>Program/script: C:\Inverter-Data-Logger\InverterExport.py</li>
<li>-&gt; OK.</li></ul>
Conditions (tab) -&gt;
<ul><li>choose your own options.</li></ul>
Settings (tab) -&gt;
<ul><li>'Allow task to be run on demand'</li>
<li>'Stop the task if it runs longer than: '2 days'</li>
<li>If the task is already running, then the following rule applies: 'Do not start a new instance'</li>
<li>-&gt; OK</li></ul></ul>
<p>NOTE: If you need to kill the process manually: open Task Manager &gt; Processes &gt; Tick 'Show Processes from all users' &gt; right click 'python.exe' &gt; select 'End Process'.</p>

<h2>Why copy config-org.cfg, can't I edit it directly?</h2><hr>
<p>Yes you can edit config-org.cfg directly. However if you want to update the script your settings will be overwritten with the default values. By creating config.cfg, you can preserve your settings when upgrading.</p>

<h2>Development</h2><hr>
<p>To help with development when no sun is present a small simulator script can be found in the folder Development. This script works by reading values from to database used by the MysqlOutput, but with the time shifted 6 hours back. To use the simulator, you should use the MysqlOutput to fill the database and configure database settings in de sim-config.cfg file.</p>
