#!/usr/bin/python

from InverterMsg import InverterMsg # Import the Msg handler

import socket               # Needed for talking to inverter
import datetime             # Used for timestamp
from os import path

# For database output
import MySQLdb as mdb       

# For PVoutput 
import urllib
import urllib2

# Unsafe but very simple config manager
from config_default import *

if path.exists('config.py'):
    from config import *

# Receive data with a socket
s = socket.socket()
s.connect((ip, port))
s.sendall('\x68\x02\x40\x30\xa6\x68\xe6\x23\xa6\x68\xe6\x23\x01\x00\xa1\x16')
data = s.recv(128)
s.close

msg = InverterMsg(data)  # This is where the magic happens ;)

now = datetime.datetime.now()


if mysql_enabled:
    print "Uploading to database"
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
    print "Uploading to PVoutput"
    url = "http://pvoutput.org/service/r2/addstatus.jsp"
    
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
    
    print response.read()                                               # Show the response
    
