import PluginLoader
import datetime
import urllib
import urllib2


class PVoutputOutput(PluginLoader.Plugin):
    """Sends the data from the inverter logger to PVoutput.org"""

    def process_message(self, msg):
        """Send the information from the inverter to PVoutput.org.

        Args:
            msg (InverterMsg.InverterMsg): Message to process

        """
        now = datetime.datetime.now()

        if (now.minute % 5) == 0:  # Only run at every 5 minute interval

            sys_id = 'sysid-'+msg.id.rstrip()
            if not self.config.has_option('pvout', sys_id):
                self.logger.error('no sysid in configuration file for inverter with ID: {0}, skipping.'.format(msg.id))
                return []

            api_key = 'apikey-'+msg.id.rstrip()
            if not self.config.has_option('pvout', api_key):
                self.logger.error('no apikey in configuration file for inverter with ID: {0}, skipping.'.format(msg.id))
                return []

            self.logger.info('Uploading data from inverter with ID: {0} to PVoutput'.format(msg.id))

            url = "http://pvoutput.org/service/r2/addstatus.jsp"

            self.logger.debug('temperature: '+str(msg.temperature)) # err:514,7
            self.logger.debug('AC1 voltage: '+str(msg.v_ac(1)))
            self.logger.debug('PV1 voltage: '+str(msg.v_pv(1)))
            self.logger.debug('e_today    : '+str(msg.e_today))
            self.logger.debug('e_total    : '+str(msg.e_total))
            self.logger.debug('total E    : '+str(((((msg.e_today*10)-(int(msg.e_today*10)))/10)+msg.e_total)))

            get_data = {
                'key': self.config.get('pvout', api_key),
                'sid': self.config.get('pvout', sys_id),
                'd': now.strftime('%Y%m%d'),
                't': now.strftime('%H:%M'),
                'v1': msg.e_today * 1000,
                'v2': msg.p_ac(1),
            }
            # sometimes the inverter gives 514,7 as temperature, don't send temp then!
            if (msg.temperature<300 and self.config.getboolean('general', 'use_temperature')):
                get_data.update ({
                    'v5': msg.temperature,
                })
            else: self.logger.error('temperature out of range: '+str(msg.temperature))

            get_data.update ({
                'v6': msg.v_pv(1)
            })    

            get_data_encoded = urllib.urlencode(get_data)
            self.logger.debug(url + '?' + get_data_encoded)
            request_object = urllib2.Request(url + '?' + get_data_encoded)
            try:
                response = urllib2.urlopen(request_object)
            except urllib2.HTTPError, e:
                self.logger.error('HTTP error : '+str(e.code)+' Reason: '+str(e.reason))
                return []
            except urllib2.URLError, e:
                self.logger.error('URL error : '+str(e.args)+' Reason: '+str(e.reason))
                return []
            else:
                self.logger.debug(response.read())  # Show the response

        self.logger.error('Not sending to PVoutput, not within 5 minutes interval.')
