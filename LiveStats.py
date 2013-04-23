#!/usr/bin/python

from InverterMsg import InverterMsg # Import the Msg handler

import socket               # Needed for talking to inverter
import datetime             # Used for timestamp


################
### Settings ###
################

# Inverter
ip = '192.168.1.15'
port = 8899

#######################
### End of Settings ###
#######################

s = socket.socket()                                                     # Create a socket object
s.connect((ip, port))
s.sendall('\x68\x02\x40\x30\xa6\x68\xe6\x23\xa6\x68\xe6\x23\x01\x00\xa1\x16')
data = s.recv(128)
s.close                                                                 # Close the socket when done

msg = InverterMsg(data)  # This is where the magic happens ;)
print "ID: {0}".format(msg.getID())

print "E Today: {0:>5}   Total: {1:<5}".format(msg.getEToday(), msg.getETotal())
print "H Total: {0:>5}   Temp:  {1:<5}".format(msg.getHTotal(), msg.getTemp())

print "PV1   V: {0:>5}   I: {1:>4}".format(msg.getVPV(1), msg.getIPV(1))
print "PV2   V: {0:>5}   I: {1:>4}".format(msg.getVPV(2), msg.getIPV(2))
print "PV3   V: {0:>5}   I: {1:>4}".format(msg.getVPV(3), msg.getIPV(3))

print "L1    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}".format(msg.getPAC(1), msg.getVAC(1), msg.getIAC(1), msg.getFAC(1)) 
print "L2    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}".format(msg.getPAC(2), msg.getVAC(2), msg.getIAC(2), msg.getFAC(2)) 
print "L3    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}".format(msg.getPAC(3), msg.getVAC(3), msg.getIAC(3), msg.getFAC(3)) 
