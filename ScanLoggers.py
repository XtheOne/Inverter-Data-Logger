#!/usr/bin/python
"""Logger search program.

Find an IGEN Wi-Fi kit logger and query the connected inverter(s).
"""
import socket  # Needed for talking to logger
import struct
import sys
import InverterMsg  # Import the Msg handler
import InverterLib  # Import the library

def get_inverter_sn(logger_sn, logger_ip):
    data = InverterLib.createV4RequestFrame(int(logger_sn))
#    print >>sys.stdout, 'DATA = %s' % data
    logger_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger_socket.settimeout(3)
    # Connect the socket to the port where the server is listening
    logger_socket.connect((logger_ip, 8899))
    logger_socket.sendall(data)

    print >>sys.stdout, 'Listing Inverter(s) connected to this WiFi logger'
    okflag = False
    while (not okflag):
        data = logger_socket.recv(1500)
        msg = InverterMsg.InverterMsg(data)

        if (msg.msg)[:9] == 'DATA SEND':
            logger_socket.close()
            okflag = True
            continue

        print >>sys.stdout, 'Inverter SN = %s' % msg.id
        print >>sys.stdout, 'Inverter main firmware version: = %s' % msg.main_fwver
        print >>sys.stdout, 'Inverter slave firmware version: = %s' % msg.slave_fwver

    logger_socket.close()

#main
sys.stdout.write('This script will look for iGEN WiFi Kit loggers from SolarMAN PV\n')
sys.stdout.write('List their IPs and S/Ns and connected inverters S/N\n')
sys.stdout.write('These loggers are found in Omnik, Hosola, Ginlong, Kstar, Seasun, SolaX, Samil, Sofar, Trannergy\n')
sys.stdout.write('and other Solar inverters\n')

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((InverterLib.getNetworkIp(), 48899))
# Set a timeout so the socket does not block indefinitely when trying to receive data.
sock.settimeout(6)
# Set the time-to-live for messages to 1 so they do not go past the local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
SendData = "WIFIKIT-214028-READ" # Lotto/TM = "AT+YZAPP=214028,READ"
try:
    # Send data to the broadcast address
    sent = sock.sendto(SendData.encode('utf-8'), ('<broadcast>', 48899))
    # Look for responses from all recipients
    while True:
        try:
            data, server = sock.recvfrom(1500)
        except socket.timeout:
            break
        else:
            if (data == SendData.encode('utf-8')): continue #skip sent data
            a = data.split(b',')
            logger_ip, logger_mac, logger_sn = a[0],a[1],a[2]
            sys.stdout.write('WiFi kit logger found, IP = %s and S/N = %s\n' % (logger_ip, logger_sn))
            data = InverterLib.createV4RequestFrame(int(logger_sn))
            logger_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger_socket.settimeout(3)
            # Connect the socket to the port where the server is listening
            logger_socket.connect((logger_ip, 8899))
            logger_socket.sendall(data)
        
            sys.stdout.write('Listing Inverter(s) connected to this WiFi logger\n')
            okflag = False
            while (not okflag):
                data = logger_socket.recv(1500)
                msg = InverterMsg.InverterMsg(data)
        
                if (msg.msg)[:9] == 'DATA SEND':
                    logger_socket.close()
                    okflag = True
                    continue
        
                sys.stdout.write('Inverter SN = %s\n' % msg.id)
                sys.stdout.write('Inverter main firmware version: = %s\n')
                sys.stdout.write('Inverter slave firmware version: = %s\n' % msg.slave_fwver)
        
            logger_socket.close()

finally:
    sys.stdout.write('closing socket, scanning done!\n')
    sock.close()
    sys.stdout.flush()
