import SocketServer
import struct
import ConfigParser, os
import MySQLdb as mdb

'''
    Functions to convert the values to their binary representation 
'''
def packShort(data):
    if data == -1 or data == -10 or data == -100: # The omnik uses 65535 as -1
        data = 65535
    return struct.pack('!H', data);

def packLong(data):
    return struct.pack('!I', data);


'''
    Class to send the simulated inverter messages
'''
class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        print self.client_address[0] + ' connected'
        self.data = ''
        while 1:
            data = self.request.recv(1024)
            if not data: break  # if no data is received, break and close the connection
            
            self.data += data
            self.data = self.data[-16:]
            '''
            If the 16 byte string starts with a specific binary string assume the rest is ok. No need
            to check if the serial matches.
            '''            
            if self.data[:4] == '\x68\x02\x40\x30':
                with con: 
                    cur = con.cursor(mdb.cursors.DictCursor)
                    cur.execute("SELECT * FROM minutes WHERE ServerStamp > NOW() - INTERVAL 6 HOUR - INTERVAL 5 MINUTE LIMIT 0, 1")
                    rows = cur.fetchall()
                    row = rows[0]
                
                print 'Request at ' + row['ServerStamp'].strftime('%Y-%m-%d %H:%M:%S')    
                
                # Create InverterMsg
                data2 = 'hUA\xb0\xa6h\xe6#\xa6h\xe6#\x81\x02\x01' + row['InvID'] + packShort(row['Temp']*10) \
                    + packShort(row['VPV1']*10) + packShort(row['VPV2']*10) + packShort(row['VPV3']*10) \
                    + packShort(row['IPV1']*10) + packShort(row['IPV2']*10) + packShort(row['IPV3']*10) \
                    + packShort(row['IAC1']*10) + packShort(row['IAC2']*10) + packShort(row['IAC3']*10) \
                    + packShort(row['VAC1']*10) + packShort(row['VAC2']*10) + packShort(row['VAC3']*10) \
                    + packShort(row['FAC1']*100) + packShort(row['PAC1'])  \
                    + packShort(row['FAC2']*100) + packShort(row['PAC2'])  \
                    + packShort(row['FAC3']*100) + packShort(row['PAC3'])  \
                    + packShort(row['EToday']*100) \
                    + packLong(row['ETotal']*10) \
                    + packLong(row['HTotal']) \
                    + '\x00\x01\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00&\x16h\x11A\xf0\xa6h\xe6#\xa6h\xe6#DATA SEND IS OK\r\na\x16\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                self.request.sendall(data2) # Send the message 

        print self.client_address[0] + ' disconnected'
        self.request.close()
        
        
if __name__ == "__main__":
    # Load the setting
    mydir = os.path.dirname(os.path.abspath(__file__))
    
    config = ConfigParser.RawConfigParser()
    config.read([mydir + '/sim-config-default.cfg', mydir + '/sim-config.cfg'])
    
    con = mdb.connect(config.get('mysql','mysql_host'), config.get('mysql','mysql_user'),
                       config.get('mysql','mysql_pass'), config.get('mysql','mysql_db'))
    
    HOST, PORT = config.get('simulator','ip'), config.getint('simulator','port')
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

