import struct               # Converting bytes to numbers

class InverterMsg:
    'Class for Inverter message'
    rawmsg = ""
    
    def __init__(self, msg, offset=0):
        self.rawmsg = msg
        self.offset = offset
        
    def __getString(self, begin, end):
        return self.rawmsg[begin:end]
    
    def __getShort(self, begin, devider=10):
        num = struct.unpack('!H', self.rawmsg[begin:begin+2])[0]
        if num == 65535:
            return -1
        else:
            return float(num)/devider
        
    def __getLong(self, begin, devider=10):
        return float(struct.unpack('!I', self.rawmsg[begin:begin+4])[0])/devider
        
    def getID(self):
        return self.__getString(15,31)

    def getTemp(self):
        return self.__getShort(31)
    
    def getPower(self):
        print self.__getShort(59)
        
    def getETotal(self):
        return self.__getLong(71)
        
    def getVPV(self, i=1):
        if i  not in range(1, 4):
            i = 1
        num = 33 + (i-1)*2
        return self.__getShort(num)
        
    def getIPV(self, i=1):
        if i not in range(1, 4):
            i=1
        num = 39 + (i-1)*2
        return self.__getShort(num)
    
    def getIAC(self, i=1):
        if i not in range(1, 4):
            i=1
        num = 45 + (i-1)*2
        return self.__getShort(num)
        
    def getVAC(self, i=1):
        if i not in range(1, 4):
            i=1
        num = 51 + (i-1)*2
        return self.__getShort(num)  

    def getFAC(self, i=1):
        if i not in range(1, 4):
            i=1
        num = 57 + (i-1)*4
        return self.__getShort(num, 100)          

    def getPAC(self, i=1):
        if i not in range(1, 4):
            i=1
        num = 59 + (i-1)*4
        return int(self.__getShort(num, 1)) # Don't divide
    
    def getEToday(self):
        return self.__getShort(69, 100)     # Devide by 100

    def getHTotal(self):
        return int(self.__getLong(75, 1))  # Don't divide
