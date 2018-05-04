#!/usr/bin/python
"""InverterExport program.

Get data from a Wi-Fi kit logger and save/send the data to the defined plugin(s)
"""
import socket  # Needed for talking to logger
import sys
import logging
import logging.config
import sys
if sys.version[:1] == '2':
    import ConfigParser as configparser
else:
    import configparser
import optparse
import os
import re
import errno
from PluginLoader import Plugin
import InverterMsg  # Import the Msg handler
import InverterLib  # Import the library

class InverterExport(object):
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

        self.config = configparser.RawConfigParser()
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
        if not self.config.has_option('server', 'listen_address'):
            self.logger.error('no listen address defined in configuration file, exiting.')
            return []

        if not self.config.has_option('server', 'listen_port'):
            self.logger.error('no listen port defined in configuration file, exiting.')
            return []

        port = int(self.config.get('server', 'listen_port'))
        liip = self.config.get('server', 'listen_address')

        self.logger.info('Start listening on IP: {0} and Port {1}'.format(liip, port))
        self.logger.info('Use CTRL-Break to exit.')

        logger_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger_socket.bind((liip, port))
        logger_socket.listen(1)

        while (True):
            # Wait for a connection
            self.logger.debug('waiting for a connection.')
            conn,addr = logger_socket.accept()
    
            self.logger.debug('connection from: {0}'.format(addr))
    
            okflag = False
            while (not okflag):
                try:
                    data = conn.recv(1024)
                    #when disconnected
                    if(len(data) == 0):
                        self.logger.debug('Socket disconnected')
                        okflag = True
                        continue

                except socket.error as e:
                    err = e.args[0]
                    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                        sleep(1)
                        self.logger.error('No data available. err = {0}'.format(err))
                        okflag = True
                        continue
                    else:
                        # a "real" error occurred
                        self.logger.error('Socket error. err = {0}'.format(err))
                        okflag = True
                        continue
    
                if(len(data) < 13):
                    self.logger.error("Too short frame received: {0} bytes".format(len(data)))
                    okflag = True
                    continue
    
                #dump raw data to log
                self.logger.debug('RAW received Packet (len={0}): '.format(len(data))+':'.join(hex(ord(chr(x)))[2:].zfill(2) for x in bytearray(data))+'  '+re.sub('[^\x20-\x7f]', '', ''.join(chr(x) for x in bytearray(data))))
    
                msg = InverterMsg.InverterMsg(data)
    
                #log DATA length
                self.logger.debug('DATA len={0}: '.format(msg.len))
    
                if (msg.msg)[:9] == 'DATA SEND':
                    self.logger.debug("Exit Status: {0}".format(msg.msg))
                    okflag = True
                    continue
    
                if (msg.msg)[:11] == 'NO INVERTER':
                    self.logger.debug("Inverter is in sleep mode: {0} received".format(msg.msg))
                    okflag = True
                    continue
    
                self.logger.info("Inverter ID: {0}".format(msg.id))
                if (msg.len > 140):
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
            config: configparser with settings from file
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
                'InverterLogger': {
                    'handlers': config.get('log', 'type').split(','),
                    'level': log_levels[config.get('log', 'level')]
                }
            }
        }
        logging.config.dictConfig(log_dict)
        self.logger = logging.getLogger('InverterLogger')

    def override_config(self, section, option, value):
        """Override config settings"""
        self.config.set(section, option, value)

if __name__ == "__main__":
    inverter_exporter = InverterExport('config.cfg')
    inverter_exporter.run()
