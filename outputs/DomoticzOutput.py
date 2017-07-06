import PluginLoader
import datetime
import urllib
import urllib2


class DomoticzOutput(PluginLoader.Plugin):
    """Sends the data from the Omnik inverter to Domoticz."""

    def process_message(self, msg):
        """Send the information from the inverter to Domoticz.

        Args:
            msg (InverterMsg.InverterMsg): Message to process

        """
        self.logger.info('Uploading to Domoticz')

        host = self.config.get('domoticz', 'host')
        port = self.config.get('domoticz', 'port')
        path = self.config.get('domoticz', 'path')

        url = ("http://" + host + ":" + port + path)
        self.logger.debug('url: '+url)

# the inverter gives 0 for voltage and current when in sleep mode, don't sent those values then to keep the graphs neat.
        data_idx_array = {
            self.config.get('domoticz', 'string1current_idx'): msg.i_pv(1),
            self.config.get('domoticz', 'string2current_idx'): msg.i_pv(2),
            self.config.get('domoticz', 'AC_current_idx'): msg.i_ac(1),
            self.config.get('domoticz', 'Power_Lifetimeenergy_idx'): str(msg.p_ac(1))+';'+str(((((msg.e_today*10)-(int(msg.e_today*10)))/10)+msg.e_total)*1000),
        }
        if (msg.temperature<300): # sometimes the inverter gives 514,7 as temperature, don't send temp then!
            data_idx_array.update ({
                self.config.get('domoticz', 'temp_idx'): msg.temperature,
            })
        else: self.logger.debug('temperature out of range: '+str(msg.temperature))
        if (msg.v_pv(1)>0):
            data_idx_array.update ({
                self.config.get('domoticz', 'string1voltage_idx'): msg.v_pv(1),
            })
        else: self.logger.debug('PV1 voltage out of range: '+str(msg.v_pv(1)))
        if (msg.v_pv(2)>0):
            data_idx_array.update ({
                self.config.get('domoticz', 'string2voltage_idx'): msg.v_pv(2),
            })
        else: self.logger.debug('PV2 voltage out of range: '+str(msg.v_pv(2)))
        if (msg.v_ac(1)>0): # drops to 0V when in sleep mode
            data_idx_array.update ({
                self.config.get('domoticz', 'AC_voltage_idx'): msg.v_ac(1),
            })
        else: self.logger.debug('AC voltage out of range: '+str(msg.v_ac(1)))

        for idx, value in data_idx_array.items():
            get_data = {
                'svalue': value,
                'type': 'command',
                'param': 'udevice',
                'idx' : idx,
                'nvalue': '0'
                }

            get_data_encoded = urllib.urlencode(get_data)
            self.logger.debug(url + '?' + get_data_encoded)
            request_object = urllib2.Request(url + '?' + get_data_encoded)
            try:
                response = urllib2.urlopen(request_object)
            except urllib2.HTTPError, e:
                self.logger.debug('HTTP error : '+str(e.code)+' Reason: '+str(e.reason))
            else:
                self.logger.debug(response.read())  # Show the response
