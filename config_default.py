# Copy this file to config.py and adjust the values of the fields. The 
# values in this file are then overwritten with the ones in config.py.


################
### Settings ###
################

# Inverter
ip = '192.168.1.15'             # IP address of your Omnik inverter
port = 8899                     # Default for a Omnik with Wifi module

# Mysql export
mysql_enabled = False           # Enable for exporting to a mysql database
mysql_host = '127.0.0.1'        # Host where the mysql server is active
mysql_user = ''                 # Username
mysql_pass = ''                 # Password
mysql_db   = ''                 # The name of the database

# PVoutput
pvout_enabled = False            # Enable or disable uploading to PVoutput
pvout_apikey = 'NOTAREALAPIKEY0wajklfsda90ifklfeaf' # These two can be found at http://pvoutput.org/account.jsp
pvout_sysid  = 12345
