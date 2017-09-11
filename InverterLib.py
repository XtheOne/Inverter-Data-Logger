import socket

def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

def generate_string(serial_no):
    """Create request string for inverter.

    The request string is build from several parts. The first part is a
    fixed 4 char string; the second part is the reversed hex notation of
    the s/n twice; then again a fixed string of two chars; a checksum of
    the double s/n with an offset; and finally a fixed ending char.

    Args:
        serial_no (int): Serial number of the inverter

    Returns:
        str: Information request string for inverter
    """
    #response = '\x68\x02\x40\x30' # Old
    response = '\x68\x02\x41\xb1' #from SolarMan / new Omnik
    res_ck = sum([ord(c) for c in response])
    footer = '\x01\x00' # x02\x00 geeft ERR= -1
    foo_ck = sum([ord(c) for c in footer])
    double_hex = hex(serial_no)[2:] * 2
    hex_list = [double_hex[i:i + 2].decode('hex') for i in
                reversed(range(0, len(double_hex), 2))]
    cs_count = 152 + res_ck + foo_ck + sum([ord(c) for c in hex_list])
    checksum = hex(cs_count)[-2:].decode('hex')
    response += ''.join(hex_list) + footer + checksum + '\x16'
    return response
