#!/usr/bin/python
"""Logger search program.

Find an IGEN Wi-Fi kit logger and query the connected inverter(s).
"""
import socket  # Needed for talking to logger
import struct
import sys
import InverterMsg  # Import the Msg handler
import InverterLib  # Import the library

def get_inverter_sn(wifi_serial, wifi_ip):
    data = InverterLib.generate_string(int(wifi_serial))
#    print >>sys.stdout, 'DATA = %s' % data
    logger_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger_socket.settimeout(3)
    # Connect the socket to the port where the server is listening
    logger_socket.connect((wifi_ip, 8899))
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
print >>sys.stdout, 'This script will look for iGEN WiFi Kit loggers from SolarMAN PV'
print >>sys.stdout, 'List their IPs and S/Ns and connected inverters S/N'
print >>sys.stdout, 'These loggers are found in Omnik, Hosola, Ginlong, Kstar, Seasun, SolaX, Samil, Sofar, Trannergy'
print >>sys.stdout, 'and other Solar inverters'

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
    sent = sock.sendto(SendData, ('<broadcast>', 48899))
    # Look for responses from all recipients
    while True:
        try:
            data, server = sock.recvfrom(1500)
        except socket.timeout:
            break
        else:
            if (data == SendData): continue #skip sent data
            a = data.split(',')
            wifi_ip, wifi_mac, wifi_sn = a[0],a[1],a[2]
            print >>sys.stdout, 'WiFi kit logger found, IP = %s and S/N = %s' % (wifi_ip, wifi_sn)
            data = InverterLib.generate_string(int(wifi_sn))
            logger_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger_socket.settimeout(3)
            # Connect the socket to the port where the server is listening
            logger_socket.connect((wifi_ip, 8899))
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

finally:
    print >>sys.stdout, 'closing socket, scanning done!'
    sock.close()
