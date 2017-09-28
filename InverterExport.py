#!/usr/bin/python
"""OmnikExport program.

Get data from a Wi-Fi kit logger and save/send the data to the defined plugin(s)
"""
import socket  # Needed for talking to logger
import sys
import logging
import logging.config
import ConfigParser
import optparse
import os
from PluginLoader import Plugin
import InverterMsg  # Import the Msg handler
import InverterLib  # Import the library

class OmnikExport(object):
    """
    Get data from the inverter(s) and store the data in a configured output
    format/location.

    """

    config = None
    logger = None

    def __init__(self, config_file):
        # Load the setting
        config_files = [InverterLib.expand_path('config-default.cfg'),
                        InverterLib.expand_path(config_file)]

        self.config = ConfigParser.RawConfigParser()
        self.config.read(config_files)

        # add command line option -p / --plugins to override the output plugins used
        parser = optparse.OptionParser()
        parser.add_option('-p', '--plugins',
                action="store", dest="plugins",
                help="output plugins to use")

        self.options, self.args = parser.parse_args()

    def run(self):
        """Get information from inverter and store is configured outputs."""

        self.build_logger(self.config)

        # Load output plugins
        # Prepare path for plugin loading
        sys.path.append(InverterLib.expand_path('outputs'))

        Plugin.config = self.config
        Plugin.logger = self.logger

        enabled_plugins = self.config.get('general', 'enabled_plugins')\
                                     .split(',')
        
        # if -p / --plugin option giving at command line, override enabled plugins
        if self.options.plugins:
            enabled_plugins = self.options.plugins.split(',')
        
        for plugin_name in enabled_plugins:
            plugin_name = plugin_name.strip()
            self.logger.debug('Importing output plugin ' + plugin_name)
            __import__(plugin_name)

        # Connect to logger
        if not self.config.has_option('logger', 'gateways'):
            self.logger.error('no gateways defined in configuration file, exiting.')
            return []

        if(self.config.get('logger', 'gateways') == 'auto'):
            # get loggers
            gateway_list = InverterLib.getLoggers().split(',')
            if (len(gateway_list) < 2):
                self.logger.error('No loggers found: {0}, exiting.'.format(gateway_list))
                return []
            self.logger.info('Loggers found  on the network: {0}.'.format(gateway_list))
        else:
            gateway_list = self.config.get('logger', 'gateways').split(',')
            if (len(gateway_list) % 2):
                self.logger.error('incorrect number of values in configuration file for gateways: {0}, exiting.'.format(gateway_list))
                return []

        for i in range(0, len(gateway_list), 2):
            ip = gateway_list[i]
            sn = gateway_list[i+1]
    
            self.logger.info('Connecting to logger with IP: {0} and SN {1}'.format(ip, sn))
    
            port = self.config.get('logger', 'port')
            timeout = self.config.getfloat('logger', 'timeout')
    
            next = False
            for res in socket.getaddrinfo(ip, port, socket.AF_INET,
                                           socket.SOCK_STREAM):
                 family, socktype, proto, canonname, sockadress = res
                 try:
                     self.logger.info('connecting to {0} port {1}'.format(ip, port))
                     logger_socket = socket.socket(family, socktype, proto)
                     logger_socket.settimeout(timeout)
                     logger_socket.connect(sockadress)
                 except socket.error as msg:
                     self.logger.error('Could not open socket')
                     self.logger.error(msg)
                     self.logger.error('Error connecting to logger with IP: {0} and SN {1}, trying next logger.'.format(ip, sn))
                     next = True
                     break
            if (next):
                continue

            data = InverterLib.generate_string(int(sn))
            logger_socket.sendall(data)
    
            #dump raw data to log
            self.logger.debug('RAW sent Packet (len={0}): '.format(len(data))+':'.join(x.encode('hex') for x in data))
    
            okflag = False
            while (not okflag):
    
                try:
                    data = logger_socket.recv(1024)
                except socket.timeout, e:
                    self.logger.error('Timeout connecting to logger with IP: {0} and SN {1}, trying next logger.'.format(ip, sn))
                    okflag = True
                    continue
        
                #dump raw data to log
                self.logger.debug('RAW received Packet (len={0}): '.format(len(data))+':'.join(x.encode('hex') for x in data))
        
                msg = InverterMsg.InverterMsg(data)

                #log DATA length
                self.logger.debug('DATA len={0}: '.format(msg.len))

                if (msg.msg)[:9] == 'DATA SEND':
                    self.logger.debug("Exit Status: {0}".format(msg.msg))
                    logger_socket.close()
                    okflag = True
                    continue
    
                if (msg.msg)[:11] == 'NO INVERTER':
                    self.logger.debug("Inverter(s) are in sleep mode: {0} received".format(msg.msg))
                    logger_socket.close()
                    okflag = True
                    continue
    
                self.logger.info("Inverter ID: {0}".format(msg.id))
                self.logger.info("Inverter main firmware version: {0}".format(msg.main_fwver))
                self.logger.info("Inverter slave firmware version: {0}".format(msg.slave_fwver))
                self.logger.info("RUN State: {0}".format(msg.run_state))
        
                for plugin in Plugin.plugins:
                    self.logger.debug('Run plugin' + plugin.__class__.__name__)
                    plugin.process_message(msg)
    
    def build_logger(self, config):
        # Build logger
        """
        Build logger for this program


        Args:
            config: ConfigParser with settings from file
        """
        log_levels = dict(notset=0, debug=10, info=20, warning=30, error=40, critical=50)
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
                    'filename': InverterLib.expand_path(config.get('log',
                                                              'filename')),
                    'formatter': 'f'},
            },
            'loggers': {
                'OmnikLogger': {
                    'handlers': config.get('log', 'type').split(','),
                    'level': log_levels[config.get('log', 'level')]
                }
            }
        }
        logging.config.dictConfig(log_dict)
        self.logger = logging.getLogger('OmnikLogger')

    def override_config(self, section, option, value):
        """Override config settings"""
        self.config.set(section, option, value)

if __name__ == "__main__":
    omnik_exporter = OmnikExport('config.cfg')
    omnik_exporter.run()
