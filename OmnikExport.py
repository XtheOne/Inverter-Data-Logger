#!/usr/bin/python

import InverterMsg      # Import the Msg handler

import socket               # Needed for talking to inverter
import datetime             # Used for timestamp
import sys
import logging
import logging.config
import ConfigParser, os

from PluginLoader import Plugin

# For PVoutput
import urllib, urllib2

# Load the setting
mydir = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser.RawConfigParser()
config.read([mydir + '/config-default.cfg', mydir + '/config.cfg'])

# Receive data with a socket
ip              = config.get('inverter','ip')
port            = config.get('inverter','port')
use_temp        = config.getboolean('inverter','use_temperature')
wifi_serial     = config.getint('inverter', 'wifi_sn')

pvout_enabled   = config.getboolean('pvout','pvout_enabled')
pvout_apikey    = config.get('pvout','pvout_apikey')
pvout_sysid     = config.get('pvout','pvout_sysid')

server_address = ((ip, port))

# Build logger
log_levels = dict(debug=10, info=20, warning=30, error=40, critical=50)
log_dict = dict(version=1,
                formatters={
                    'f': {'format': '%(asctime)s %(levelname)s %(message)s'}
                },
                handlers={
                    'none': {'class': 'logging.NullHandler'},
                    'console': {'class': 'logging.StreamHandler',
                                'formatter': 'f'},
                    'file': {'class': 'logging.FileHandler',
                             'filename': mydir + '/' + config.get('log', 'filename'),
                             'formatter': 'f'},
                },
                loggers={'OmnikLogger': {
                        'handlers': config.get('log', 'type').split(),
                        'level': log_levels[config.get('log', 'level')]}
                })

logging.config.dictConfig(log_dict)
logger = logging.getLogger('OmnikLogger')

# Load output plugins
# Prepare path for plugin loading
sys.path.append('outputs')

Plugin.config = config
Plugin.logger = logger
for plugin_name in config.get('general', 'enabled_plugins').split(','):
    plugin_name = plugin_name.strip()
    logger.debug('Importing output plugin ' + plugin_name)
    __import__(plugin_name)


for res in socket.getaddrinfo(ip, port, socket.AF_INET , socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        logger.info('connecting to %s port %s' % server_address)
        s = socket.socket(af, socktype, proto)
        s.settimeout(10)
    except socket.error as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break
    
if s is None:
    logger.error('could not open socket')
    sys.exit(1)
    
s.sendall(InverterMsg.generate_string(wifi_serial))
data = s.recv(1024)
s.close()

msg = InverterMsg.InverterMsg(data)  # This is where the magic happens ;)
now = datetime.datetime.now()

logger.info("ID: {0}".format(msg.getID()))

for plugin in Plugin.plugins:
    logger.debug('Run plugin' + plugin.__class__.__name__)
    plugin.process_message(msg)


if pvout_enabled and (now.minute % 5) == 0:
    logger.info('Uploading to PVoutput')
    url = "http://pvoutput.org/service/r2/addstatus.jsp"
    
    if use_temp:
        get_data = {
            'key': pvout_apikey, 
            'sid': pvout_sysid, 
            'd': now.strftime('%Y%m%d'),
            't': now.strftime('%H:%M'),
            'v1': msg.getEToday() * 1000,
            'v2': msg.getPAC(1),
            'v5': msg.getTemp(),
            'v6': msg.getVPV(1)
        }
    else:
        get_data = {
            'key': pvout_apikey, 
            'sid': pvout_sysid, 
            'd': now.strftime('%Y%m%d'),
            't': now.strftime('%H:%M'),
            'v1': msg.getEToday() * 1000,
            'v2': msg.getPAC(1),
            'v6': msg.getVPV(1)
        }

    get_data_encoded = urllib.urlencode(get_data)                       # UrlEncode the parameters
    
    request_object = urllib2.Request(url + '?' + get_data_encoded)      # Create request object
    response = urllib2.urlopen(request_object)                          # Make the request and store the response

    logger.info(response.read())                                               # Show the response
    
