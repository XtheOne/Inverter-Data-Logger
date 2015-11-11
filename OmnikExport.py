#!/usr/bin/python

import InverterMsg      # Import the Msg handler

import socket               # Needed for talking to inverter
import datetime             # Used for timestamp
import sys
import logging
import logging.config
import ConfigParser
import os

from PluginLoader import Plugin

# For PVoutput
import urllib
import urllib2


class OmnikExport(object):

    @staticmethod
    def run():
        # Load the setting
        mydir = os.path.dirname(os.path.abspath(__file__))

        config = ConfigParser.RawConfigParser()
        config.read([mydir + '/config-default.cfg', mydir + '/config.cfg'])

        # Receive data with a socket
        ip = config.get('inverter', 'ip')
        port = config.get('inverter', 'port')
        use_temp = config.getboolean('inverter', 'use_temperature')
        wifi_serial = config.getint('inverter', 'wifi_sn')

        server_address = (ip, port)

        # Build logger
        log_levels = dict(debug=10, info=20, warning=30, error=40, critical=50)
        log_dict = dict(version=1,
                        formatters={
                            'f': {'format': '%(asctime)s %(levelname)s %(message)s'}
                        },
                        handlers={
                            'none': {'class': 'logging.NullHandler'},
                            'console': {'class': 'logging.StreamHandler',
                                        'formatter': 'f'},
                            'file': {'class': 'logging.FileHandler',
                                     'filename': mydir + '/' + config.get('log', 'filename'),
                                     'formatter': 'f'},
                        },
                        loggers={'OmnikLogger': {
                                'handlers': config.get('log', 'type').split(),
                                'level': log_levels[config.get('log', 'level')]}
                        })

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


        for res in socket.getaddrinfo(ip, port, socket.AF_INET, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                logger.info('connecting to %s port %s' % server_address)
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
            logger.error('could not open socket')
            sys.exit(1)

        s.sendall(InverterMsg.generate_string(wifi_serial))
        data = s.recv(1024)
        s.close()

        msg = InverterMsg.InverterMsg(data)
        now = datetime.datetime.now()

        logger.info("ID: {0}".format(msg.getID()))

        for plugin in Plugin.plugins:
            logger.debug('Run plugin' + plugin.__class__.__name__)
            plugin.process_message(msg)

if __name__ == "__main__":
    OmnikExport.run()
