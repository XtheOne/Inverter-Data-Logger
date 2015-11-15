#!/usr/bin/python

import InverterMsg  # Import the Msg handler
import OmnikExport
import sys, os
import socket               # Needed for talking to inverter
import ConfigParser

from optparse import OptionParser

parser = OptionParser()
parser.add_option("--csv", "--wsl", help="Output in csv format", action="store_true", default=False )

(options, args) = parser.parse_args()


# Load the setting
mydir = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser.RawConfigParser()
config.read([mydir + '/config-default.cfg', mydir + '/config.cfg'])

# Receive data with a socket
ip              = config.get('inverter','ip')
port            = config.get('inverter','port')
wifi_serial     = config.getint('inverter', 'wifi_sn')

log_enabled     = config.getboolean('log','log_enabled')
log_filename    = mydir + '/' + config.get('log','log_filename')


# Connect the socket to the port where the server is listening
server_address = ((ip, port))

for res in socket.getaddrinfo(ip, port, socket.AF_INET , socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print >>sys.stderr, 'connecting to %s port %s' % server_address
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
    print 'could not open socket'
    sys.exit(1)
    
s.sendall(OmnikExport.OmnikExport.generate_string(wifi_serial))
data = ''
while 1:
    data += s.recv(1024)
    if len(data) >= 198: break
s.close()

msg = InverterMsg.InverterMsg(data)  # This is where the magic happens ;)

if not options.csv:
    print "ID: {0}".format(msg.id())
    
    print "E Today: {0:>5}   Total: {1:<5}".format(msg.e_today, msg.e_total)
    print "H Total: {0:>5}   Temp:  {1:<5}".format(msg.h_total, msg.temperature)
    
    print "PV1   V: {0:>5}   I: {1:>4}".format(msg.v_pv(1), msg.i_pv(1))
    print "PV2   V: {0:>5}   I: {1:>4}".format(msg.v_pv(2), msg.i_pv(2))
    print "PV3   V: {0:>5}   I: {1:>4}".format(msg.v_pv(3), msg.i_pv(3))
    
    print "L1    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
        .format(msg.p_ac(1), msg.v_ac(1), msg.i_ac(1), msg.f_ac(1))
    print "L2    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
        .format(msg.p_ac(2), msg.v_ac(2), msg.i_ac(2), msg.f_ac(2))
    print "L3    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
        .format(msg.p_ac(3), msg.v_ac(3), msg.i_ac(3), msg.f_ac(3))
else:
    print "Id,Temp,VPV1,VPV2,VPV3,IPV1,IPV2,IPV3,IAC1,IAC2,IAC3,", \
        "VAC1,VAC2,VAC3,FAC1,PAC1,FAC2,PAC2,FAC3,PAC3,ETODAY,ETOTAL,HTOTAL"
    print ("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}," +
           "{10},{11},{12},{13},{14},{15},{16},{17},{18},{19}," +
           "{20},{21},{22}").format(msg.id(),
                                    msg.temperature(), msg.v_pv(1), msg.v_pv(2),
                                    msg.v_pv(3), msg.i_pv(1), msg.i_pv(2),
                                    msg.i_pv(3), msg.i_ac(1), msg.i_ac(2),
                                    msg.i_ac(3), msg.v_ac(1), msg.v_ac(2),
                                    msg.v_ac(3), msg.f_ac(1), msg.p_ac(1),
                                    msg.f_ac(2), msg.p_ac(2), msg.f_ac(3),
                                    msg.p_ac(3), msg.e_today, msg.e_total,
                                    msg.h_total)
