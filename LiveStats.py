#!/usr/bin/python

from InverterMsg import InverterMsg # Import the Msg handler
import sys
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

#s = socket.socket()                                                     # Create a socket object
#s.connect((ip, port))
#s.sendall('\x68\x02\x40\x30\xa6\x68\xe6\x23\xa6\x68\xe6\x23\x01\x00\xa1\x16')
#data = s.recv(128)
#s.close                                                                 # Close the socket when done

# Create a TCP/IP socket
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ((ip, port))
message =      '\x68\x02\x40\x30\xcb\x64\xec\x23\xcb\x64\xec\x23\x01\x00\xef\x16'


for res in socket.getaddrinfo(ip, port, socket.AF_INET , socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print >>sys.stderr, 'connecting to %s port %s' % server_address
        s = socket.socket(af, socktype, proto)
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
    print 'could not open socket'
    sys.exit(1)
s.sendall(message)
data = s.recv(1024)
s.close()

#print 'Received', repr(data)



#sock.sendall('\x68\x02\x40\x30\xa6\x68\xe6\x23\xa6\x68\xe6\x23\x01\x00\xa1\x16')
#data = sock.recv(128)
#sock.close

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
