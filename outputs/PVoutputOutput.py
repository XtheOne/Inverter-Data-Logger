import PluginLoader
import datetime
import urllib
import urllib2


class PVoutputOutput(PluginLoader.Plugin):
    """Sends the data from the Omnik invertor to PVoutput.org"""

    def process_message(self, msg):
        now = datetime.datetime.now()
        if (now.minute % 5) == 0:
            self.logger.info('Uploading to PVoutput')

            url = "http://pvoutput.org/service/r2/addstatus.jsp"

            if self.config.getboolean('inverter', 'use_temperature'):
                get_data = {
                    'key': self.config.get('pvout', 'apikey'),
                    'sid': self.config.get('pvout', 'sysid'),
                    'd': now.strftime('%Y%m%d'),
                    't': now.strftime('%H:%M'),
                    'v1': msg.getEToday() * 1000,
                    'v2': msg.getPAC(1),
                    'v5': msg.getTemp(),
                    'v6': msg.getVPV(1)
                }
            else:
                get_data = {
                    'key': self.config.get('pvout', 'apikey'),
                    'sid': self.config.get('pvout', 'sysid'),
                    'd': now.strftime('%Y%m%d'),
                    't': now.strftime('%H:%M'),
                    'v1': msg.getEToday() * 1000,
                    'v2': msg.getPAC(1),
                    'v6': msg.getVPV(1)
                }

            get_data_encoded = urllib.urlencode(get_data)  # UrlEncode the parameters

            request_object = urllib2.Request(url + '?' + get_data_encoded)  # Create request object
            response = urllib2.urlopen(request_object)  # Make the request and store the response

            self.logger.info(response.read())  # Show the response
