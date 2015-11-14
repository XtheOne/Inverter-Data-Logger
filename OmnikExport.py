#!/usr/bin/python
import socket               # Needed for talking to inverter
import sys
import logging
import logging.config
import ConfigParser
import os

from PluginLoader import Plugin
import InverterMsg      # Import the Msg handler

class OmnikExport(object):

    @staticmethod
    def run():
        # Load the setting
        mydir = os.path.dirname(os.path.abspath(__file__))

        config = ConfigParser.RawConfigParser()
        config.read([mydir + '/config-default.cfg', mydir + '/config.cfg'])

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

        # Connect to inverter
        ip = config.get('inverter', 'ip')
        port = config.get('inverter', 'port')

        for res in socket.getaddrinfo(ip, port, socket.AF_INET, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                logger.info('connecting to {0} port {1}'.format(ip, port))
                s = socket.socket(af, socktype, proto)
                s.settimeout(10)
                s.connect(sa)
            except socket.error as msg:
                logger.error('Could not open socket')
                logger.error(msg)
                sys.exit(1)

        wifi_serial = config.getint('inverter', 'wifi_sn')
        s.sendall(InverterMsg.generate_string(wifi_serial))
        data = s.recv(1024)
        s.close()

        msg = InverterMsg.InverterMsg(data)

        logger.info("ID: {0}".format(msg.getID()))

        for plugin in Plugin.plugins:
            logger.debug('Run plugin' + plugin.__class__.__name__)
            plugin.process_message(msg)

if __name__ == "__main__":
    OmnikExport.run()
