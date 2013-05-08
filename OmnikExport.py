#!/usr/bin/python

from InverterMsg import InverterMsg # Import the Msg handler

import socket               # Needed for talking to inverter
import datetime             # Used for timestamp
import sys
import logging
import ConfigParser, os
from os import path

# For database output
import MySQLdb as mdb       

# For PVoutput 
import urllib
import urllib2


import HexByteConversion

# Unsafe but very simple config manager
#from config_default import *

#if path.exists('config.py'):
#    from config import *
mydir = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser.RawConfigParser()
config.read(mydir + '/config.cfg')

# Receive data with a socket
ip              = config.get('inverter','ip')
port            = config.get('inverter','port')
inverter_string = HexByteConversion.HexToByte(config.get('inverter','inverter_string'))
use_temp        = config.getboolean('inverter','use_temperature')

mysql_enabled   = config.getboolean('mysql', 'mysql_enabled')
mysql_host      = config.get('mysql','mysql_host')
mysql_user      = config.get('mysql','mysql_user')
mysql_pass      = config.get('mysql','mysql_pass')
mysql_db        = config.get('mysql','mysql_db')

pvout_enabled   = config.getboolean('pvout','pvout_enabled')
pvout_apikey    = config.get('pvout','pvout_apikey')
pvout_sysid     = config.get('pvout','pvout_sysid')

log_enabled     = config.getboolean('log','log_enabled')
log_filename    = mydir + '/' + config.get('log','log_filename')


server_address = ((ip, port))
message = inverter_string

logger = logging.getLogger('OmnikLogger')
hdlr = logging.FileHandler(log_filename)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

for res in socket.getaddrinfo(ip, port, socket.AF_INET , socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        if log_enabled:
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
    if log_enabled:
        logger.error('could not open socket')
    sys.exit(1)
s.sendall(message)
data = s.recv(1024)
s.close()

msg = InverterMsg(data)  # This is where the magic happens ;)
now = datetime.datetime.now()

if log_enabled:
    logger.info("ID: {0}".format(msg.getID())) 


if mysql_enabled:
    if log_enabled:
        logger.info('Uploading to database')
    con = mdb.connect(mysql_host, mysql_user, mysql_pass, mysql_db);
    
    with con:
        cur = con.cursor()
        cur.execute("""INSERT INTO minutes 
        (InvID, timestamp, ETotal, EToday, Temp, HTotal, VPV1, VPV2, VPV3,
         IPV1, IPV2, IPV3, VAC1, VAC2, VAC3, IAC1, IAC2, IAC3, FAC1, FAC2, 
         FAC3, PAC1, PAC2, PAC3) 
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s, %s, %s);""", 
         (msg.getID(), now, msg.getETotal(), 
          msg.getEToday(), msg.getTemp(), msg.getHTotal(), msg.getVPV(1), 
          msg.getVPV(2), msg.getVPV(3), msg.getIPV(1), msg.getIPV(2), 
          msg.getIPV(3), msg.getVAC(1), msg.getVAC(2), msg.getVAC(3), 
          msg.getIAC(1), msg.getIAC(2), msg.getIAC(3), msg.getFAC(1), 
          msg.getFAC(2), msg.getFAC(3), msg.getPAC(1), msg.getPAC(2), 
          msg.getPAC(3)) );

if pvout_enabled and (now.minute % 5) == 0:
    if log_enabled:
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
    
    if log_enabled:
        logger.info(response.read())                                               # Show the response
    
