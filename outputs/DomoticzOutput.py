import PluginLoader
import datetime
import urllib
import urllib2

class DomoticzOutput(PluginLoader.Plugin):
    """Sends the data from the inverter to Domoticz."""

    def process_message(self, msg):
        """Send the information from the inverter to Domoticz.

        Args:
            msg (InverterMsg.InverterMsg): Message to process

        """
        section_id = 'domoticz-'+msg.id
        if not self.config.has_section(section_id):
            self.logger.error('no section in configuration file for inverter with ID: {0}, skipping.'.format(msg.id))
            return []

        host = self.config.get(section_id, 'host')
        port = self.config.get(section_id, 'port')
        path = self.config.get(section_id, 'path')

        self.logger.info('Uploading data from inverter with ID: {0} to Domoticz'.format(msg.id))

        #e_total is truncated to 1 digit, add 2nd digit from e_today.
        e_total = ((((msg.e_today*10)-(int(msg.e_today*10)))/10)+msg.e_total)

        # calculate total power for 3 phase inverter
        p_ac_t = 0
        if (msg.p_ac(1)<99999 and msg.p_ac(1)>0): p_ac_t = msg.p_ac(1)
        if (msg.p_ac(2)<99999 and msg.p_ac(2)>0): p_ac_t = p_ac_t + msg.p_ac(2)
        if (msg.p_ac(2)<99999 and msg.p_ac(3)>0): p_ac_t = p_ac_t + msg.p_ac(3)

        url = ("http://" + host + ":" + port + path)
        self.logger.debug('url: '+url)
        self.logger.debug('temperature   : '+str(msg.temperature)+' degrees celcius') # err:514,7
        self.logger.debug('PV1 voltage   : '+str(msg.v_pv(1))+' Volt')
        self.logger.debug('AC1 voltage   : '+str(msg.v_ac(1))+' Volt')
        self.logger.debug('AC total power: '+str(p_ac_t)+' Watt')
        self.logger.debug('e_today       : '+str(msg.e_today)+' kWh')
        self.logger.debug('msg.e_total   : '+str(msg.e_total)+' kWh')
        self.logger.debug('e_total       : '+str(e_total)+' kWh')

        # the inverter gives 0 for voltage and current when in sleep mode, don't send those values then to keep the graphs neat.
        data_idx_array = {
            self.config.get(section_id, 'Power_Lifetimeenergy_idx'): str(p_ac_t)+';'+str(e_total*1000),
        }
        # sometimes the inverter gives 514,7 as temperature, don't send temp then!
        if (msg.temperature<300 and self.config.has_option(section_id, 'temp_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'temp_idx'): msg.temperature,
            })
        else: self.logger.debug('temperature out of range, or not defined: '+str(msg.temperature)+' degrees celcius')
        # Send  e_today and e_total in Wh and h_total in h
        if (self.config.has_option(section_id, 'E_today_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'E_today_idx'): msg.e_today*1000,
            })
        else: self.logger.debug('E_today not defined: '+str(msg.e_today)+' kWh')
        if (self.config.has_option(section_id, 'E_total_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'E_total_idx'): e_total*1000,
            })
        else: self.logger.debug('E_total not defined: '+str(e_total)+' kWh')

        if (self.config.has_option(section_id, 'H_total_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'H_total_idx'): msg.h_total,
            })
        else: self.logger.debug('H_total not defined: '+str(msg.h_total)+' hours')
        # Send i_pv(1-3)
        # sometimes the inverter gives 100 as current, don't send this then!
        if (msg.i_pv(1)<30 and self.config.has_option(section_id, 'string1current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'string1current_idx'): msg.i_pv(1),
            })
        else: self.logger.debug('PV1 current out of range, or not defined: '+str(msg.i_pv(1))+' Ampere')
        if (msg.i_pv(2)<30 and self.config.has_option(section_id, 'string2current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'string2current_idx'): msg.i_pv(2),
            })
        else: self.logger.debug('PV2 current out of range, or not defined: '+str(msg.i_pv(2))+' Ampere')
        if (msg.i_pv(3)<30 and self.config.has_option(section_id, 'string3current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'string3current_idx'): msg.i_pv(3),
            })
        else: self.logger.debug('PV3 current out of range, or not defined: '+str(msg.i_pv(3))+' Ampere')
        if (self.config.has_option(section_id, 'string123current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'string123current_idx'): str(msg.i_pv(1))+';'+str(msg.i_pv(2))+';'+str(msg.i_pv(3)),
            })
        else: self.logger.debug('PV1/2/3 current not defined: '+str(msg.i_pv(1))+'/'+str(msg.i_pv(2))+'/'+str(msg.i_pv(3))+' Ampere')
        # Send v_pv(1-3)
        # don't send PV voltages when 0.
        if (msg.v_pv(1)>0 and self.config.has_option(section_id, 'string1voltage_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'string1voltage_idx'): msg.v_pv(1),
            })
        else: self.logger.debug('PV1 voltage out of range, or not defined: '+str(msg.v_pv(1))+' Volt')
        if (msg.v_pv(2)>0 and self.config.has_option(section_id, 'string2voltage_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'string2voltage_idx'): msg.v_pv(2),
            })
        else: self.logger.debug('PV2 voltage out of range, or not defined: '+str(msg.v_pv(2))+' Volt')
        if (msg.v_pv(3)>0 and self.config.has_option(section_id, 'string3voltage_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'string3voltage_idx'): msg.v_pv(3),
            })
        else: self.logger.debug('PV3 voltage out of range, or not defined: '+str(msg.v_pv(3))+' Volt')
        # Send i_ac(1-3)
        if (msg.i_ac(1)<30 and self.config.has_option(section_id, 'AC1_current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC1_current_idx'): msg.i_ac(1),
            })
        else: self.logger.debug('AC1 current out of range, or not defined: '+str(msg.i_ac(1))+' Ampere')
        if (msg.i_ac(2)<30 and self.config.has_option(section_id, 'AC2_current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC2_current_idx'): msg.i_ac(2),
            })
        else: self.logger.debug('AC2 current out of range, or not defined: '+str(msg.i_ac(2))+' Ampere')
        if (msg.i_ac(3)<30 and self.config.has_option(section_id, 'AC3_current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC3_current_idx'): msg.i_ac(3),
            })
        else: self.logger.debug('AC3 current out of range, or not defined: '+str(msg.i_ac(3))+' Ampere')
        if (self.config.has_option(section_id, 'AC123_current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC123_current_idx'): str(msg.i_ac(1))+';'+str(msg.i_ac(2))+';'+str(msg.i_ac(3)),
            })
        else: self.logger.debug('AC1/2/3 current not defined: '+str(msg.i_ac(1))+'/'+str(msg.i_ac(2))+'/'+str(msg.i_ac(3))+' Ampere')
        # Send v_ac(1-3)
        if (msg.v_ac(1)>0 and self.config.has_option(section_id, 'AC1_voltage_idx')): # drops to 0V when in sleep mode
            data_idx_array.update ({
                self.config.get(section_id, 'AC1_voltage_idx'): msg.v_ac(1),
            })
        else: self.logger.debug('AC1 voltage out of range, or not defined: '+str(msg.v_ac(1))+' Volt')
        if (msg.v_ac(2)>0 and self.config.has_option(section_id, 'AC2_voltage_idx')): # drops to 0V when in sleep mode
            data_idx_array.update ({
                self.config.get(section_id, 'AC2_voltage_idx'): msg.v_ac(2),
            })
        else: self.logger.debug('AC2 voltage out of range, or not defined: '+str(msg.v_ac(2))+' Volt')
        if (msg.v_ac(3)>0 and self.config.has_option(section_id, 'AC3_voltage_idx')): # drops to 0V when in sleep mode
            data_idx_array.update ({
                self.config.get(section_id, 'AC3_voltage_idx'): msg.v_ac(3),
            })
        else: self.logger.debug('AC3 voltage out of range, or not defined: '+str(msg.v_ac(3))+' Volt')
        # Send p_ac(1-3)
        if (msg.p_ac(1)<99999 and self.config.has_option(section_id, 'AC1_Power_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC1_Power_idx'): msg.p_ac(1),
            })
        else: self.logger.debug('AC1 power out of range, or not defined: '+str(msg.p_ac(1))+' Watt')
        if (msg.p_ac(2)<99999 and self.config.has_option(section_id, 'AC2_Power_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC2_Power_idx'): msg.p_ac(2),
            })
        else: self.logger.debug('AC2 power out of range, or not defined: '+str(msg.p_ac(2))+' Watt')
        if (msg.p_ac(3)<99999 and self.config.has_option(section_id, 'AC3_Power_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC3_Power_idx'): msg.p_ac(3),
            })
        else: self.logger.debug('AC3 power out of range, or not defined: '+str(msg.p_ac(3))+' Watt')
        # Send f_ac(1-3)
        if (msg.f_ac(1)<70 and self.config.has_option(section_id, 'AC1_frequency_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC1_frequency_idx'): msg.f_ac(1),
            })
        else: self.logger.debug('AC1 frequency out of range, or not defined: '+str(msg.f_ac(1))+' Hertz')
        if (msg.f_ac(2)<70 and self.config.has_option(section_id, 'AC2_frequency_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC2_frequency_idx'): msg.f_ac(2),
            })
        else: self.logger.debug('AC2 frequency out of range, or not defined: '+str(msg.f_ac(2))+' Hertz')
        if (msg.f_ac(3)<70 and self.config.has_option(section_id, 'AC3_frequency_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC3_frequency_idx'): msg.f_ac(3),
            })
        else: self.logger.debug('AC3 frequency out of range, or not defined: '+str(msg.f_ac(3))+' Hertz')

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
                self.logger.error('HTTP error : '+str(e.code)+' Reason: '+str(e.reason))
                return []
            except urllib2.URLError, e:
                self.logger.error('URL error : '+str(e.args)+' Reason: '+str(e.reason))
                return []
            else:
                self.logger.debug(response.read())  # Show the response
