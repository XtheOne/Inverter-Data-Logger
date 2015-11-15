#!/usr/bin/python
"""OmnikExport program.

Get data from an omniksol inverter with 602xxxxx - 606xxxx ans save the data in
a database or push to pvoutput.org.
"""
import socket  # Needed for talking to inverter
import sys
import logging
import logging.config
import ConfigParser
import os
from PluginLoader import Plugin
import InverterMsg  # Import the Msg handler


class OmnikExport(object):
    """
    Get data from Omniksol inverter and store the data in a configured output
    format/location.

    """

    @staticmethod
    def run():
        """Get information from inverter and store is configured outputs."""

        # Load the setting
        mydir = os.path.dirname(os.path.abspath(__file__))

        config = ConfigParser.RawConfigParser()
        config.read([mydir + '/config-default.cfg', mydir + '/config.cfg'])

        # Build logger
        log_levels = dict(debug=10, info=20, warning=30, error=40, critical=50)
        log_dict = {
            'version': 1,
            'formatters': {
                'f': {'format': '%(asctime)s %(levelname)s %(message)s'}
            },
            'handlers': {
                'none': {'class': 'logging.NullHandler'},
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'f'
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': mydir + '/' + config.get('log', 'filename'),
                    'formatter': 'f'},
            },
            'loggers': {
                'OmnikLogger': {
                    'handlers': config.get('log', 'type').split(),
                    'level': log_levels[config.get('log', 'level')]
                }
            }
        }

        logging.config.dictConfig(log_dict)
        logger = logging.getLogger('OmnikLogger')

        # Load output plugins
        # Prepare path for plugin loading
        sys.path.append('outputs')

        Plugin.config = config
        Plugin.logger = logger
        for plugin_name in config.get('general', 'enabled_plugins').split(','):
            plugin_name = plugin_name.strip()
            logger.debug('Importing output plugin ' + plugin_name)
            __import__(plugin_name)

        # Connect to inverter
        ip = config.get('inverter', 'ip')
        port = config.get('inverter', 'port')

        for res in socket.getaddrinfo(ip, port, socket.AF_INET,
                                      socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                logger.info('connecting to {0} port {1}'.format(ip, port))
                inverter_socket = socket.socket(af, socktype, proto)
                inverter_socket.settimeout(10)
                inverter_socket.connect(sa)
            except socket.error as msg:
                logger.error('Could not open socket')
                logger.error(msg)
                sys.exit(1)

        wifi_serial = config.getint('inverter', 'wifi_sn')
        inverter_socket.sendall(OmnikExport.generate_string(wifi_serial))
        data = inverter_socket.recv(1024)
        inverter_socket.close()

        msg = InverterMsg.InverterMsg(data)

        logger.info("ID: {0}".format(msg.id))

        for plugin in Plugin.plugins:
            logger.debug('Run plugin' + plugin.__class__.__name__)
            plugin.process_message(msg)

    @staticmethod
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
        response = '\x68\x02\x40\x30'

        double_hex = hex(serial_no)[2:] * 2
        hex_list = [double_hex[i:i + 2].decode('hex') for i in
                    reversed(range(0, len(double_hex), 2))]

        cs_count = 115 + sum([ord(c) for c in hex_list])
        checksum = hex(cs_count)[-2:].decode('hex')
        response += ''.join(hex_list) + '\x01\x00' + checksum + '\x16'
        return response


if __name__ == "__main__":
    OmnikExport.run()
