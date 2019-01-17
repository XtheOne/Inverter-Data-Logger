import PluginLoader
import datetime
import sys
if sys.version[:1] == '2':
    import urllib
    import urllib2
else:
    import urllib.request, urllib.parse, urllib.error

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

        mt = int(self.config.get('general', 'min_temp'))-0.1
        mv = int(self.config.get('general', 'min_voltage'))-0.1
        mf = int(self.config.get('general', 'min_freq'))-0.1

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
        self.logger.debug('Temperature   : '+str(msg.temperature)+' degrees celcius') # err:514,7
        self.logger.debug('PV1 voltage   : '+str(msg.v_pv(1))+' Volt')
        self.logger.debug('AC1 voltage   : '+str(msg.v_ac(1))+' Volt')
        self.logger.debug('AC total power: '+str(p_ac_t)+' Watt')
        self.logger.debug('e_today       : '+str(msg.e_today)+' kWh')
        self.logger.debug('msg.e_total   : '+str(msg.e_total)+' kWh')
        self.logger.debug('e_total       : '+str(e_total)+' kWh')

        # the inverter gives 0 for voltage and current when in sleep mode, don't send those values then to keep the graphs neat.
        data_idx_array = {
            self.config.get(section_id, 'Electric_meter_idx'): str(p_ac_t)+';'+str(e_total*1000),
        }
        # sometimes the inverter gives 514,7 as temperature, don't send temp then!
        if (mt<msg.temperature<300 and self.config.has_option(section_id, 'Temp_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'Temp_idx'): msg.temperature,
            })
        else: self.logger.debug('Temperature out of range, or not defined: '+str(msg.temperature)+' degrees celcius')
        # Send  e_today and e_total in Wh and h_total in h
        if (self.config.has_option(section_id, 'E_today_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'E_today_idx'): msg.e_today,
            })
        else: self.logger.debug('E_today not defined: '+str(msg.e_today)+' kWh')
        if (self.config.has_option(section_id, 'E_total_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'E_total_idx'): e_total,
            })
        else: self.logger.debug('E_total not defined: '+str(e_total)+' kWh')
        if (self.config.has_option(section_id, 'E_total_c_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'E_total_c_idx'): e_total*1000,
            })
        else: self.logger.debug('E_total c_not defined: '+str(e_total)+' kWh')
        if (self.config.has_option(section_id, 'H_total_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'H_total_idx'): msg.h_total,
            })
        else: self.logger.debug('H_total not defined: '+str(msg.h_total)+' hours')
        # Send i_pv(1-3)
        # sometimes the inverter gives 100 as current, don't send this then!
        if (msg.i_pv(1)<30 and self.config.has_option(section_id, 'PV1_current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'PV1_current_idx'): msg.i_pv(1),
            })
        else: self.logger.debug('PV1 current out of range, or not defined: '+str(msg.i_pv(1))+' Ampere')
        if (msg.i_pv(2)<30 and self.config.has_option(section_id, 'PV2_current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'PV2_current_idx'): msg.i_pv(2),
            })
        else: self.logger.debug('PV2 current out of range, or not defined: '+str(msg.i_pv(2))+' Ampere')
        if (msg.i_pv(3)<30 and self.config.has_option(section_id, 'PV3_current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'PV3_current_idx'): msg.i_pv(3),
            })
        else: self.logger.debug('PV3 current out of range, or not defined: '+str(msg.i_pv(3))+' Ampere')
        if (self.config.has_option(section_id, 'PV123_current_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'PV123_current_idx'): str(msg.i_pv(1))+';'+str(msg.i_pv(2))+';'+str(msg.i_pv(3)),
            })
        else: self.logger.debug('PV1/2/3 current not defined: '+str(msg.i_pv(1))+'/'+str(msg.i_pv(2))+'/'+str(msg.i_pv(3))+' Ampere')
        # Send v_pv(1-3)
        # don't send PV voltages when 0.
        if (msg.v_pv(1)>mv and self.config.has_option(section_id, 'PV1_voltage_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'PV1_voltage_idx'): msg.v_pv(1),
            })
        else: self.logger.debug('PV1 voltage out of range, or not defined: '+str(msg.v_pv(1))+' Volts')
        if (msg.v_pv(2)>mv and self.config.has_option(section_id, 'PV2_voltage_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'PV2_voltage_idx'): msg.v_pv(2),
            })
        else: self.logger.debug('PV2 voltage out of range, or not defined: '+str(msg.v_pv(2))+' Volts')
        if (msg.v_pv(3)>mv and self.config.has_option(section_id, 'PV3_voltage_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'PV3_voltage_idx'): msg.v_pv(3),
            })
        else: self.logger.debug('PV3 voltage out of range, or not defined: '+str(msg.v_pv(3))+' Volts')
        if (self.config.has_option(section_id, 'PV123_voltage_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'PV123_voltage_idx'): str(msg.v_pv(1))+';'+str(msg.v_pv(2))+';'+str(msg.v_pv(3)),
            })
        else: self.logger.debug('PV1/2/3 voltage not defined: '+str(msg.v_pv(1))+'/'+str(msg.v_pv(2))+'/'+str(msg.v_pv(3))+' Volts')
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
        if (msg.v_ac(1)>mv and self.config.has_option(section_id, 'AC1_voltage_idx')): # drops to 0V when in sleep mode
            data_idx_array.update ({
                self.config.get(section_id, 'AC1_voltage_idx'): msg.v_ac(1),
            })
        else: self.logger.debug('AC1 voltage out of range, or not defined: '+str(msg.v_ac(1))+' Volt')
        if (msg.v_ac(2)>mv and self.config.has_option(section_id, 'AC2_voltage_idx')): # drops to 0V when in sleep mode
            data_idx_array.update ({
                self.config.get(section_id, 'AC2_voltage_idx'): msg.v_ac(2),
            })
        else: self.logger.debug('AC2 voltage out of range, or not defined: '+str(msg.v_ac(2))+' Volt')
        if (msg.v_ac(3)>mv and self.config.has_option(section_id, 'AC3_voltage_idx')): # drops to 0V when in sleep mode
            data_idx_array.update ({
                self.config.get(section_id, 'AC3_voltage_idx'): msg.v_ac(3),
            })
        else: self.logger.debug('AC3 voltage out of range, or not defined: '+str(msg.v_ac(3))+' Volt')
        if (self.config.has_option(section_id, 'AC123_voltage_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC123_voltage_idx'): str(msg.v_ac(1))+';'+str(msg.v_ac(2))+';'+str(msg.v_ac(3)),
            })
        else: self.logger.debug('AC1/2/3 voltage not defined: '+str(msg.v_ac(1))+'/'+str(msg.v_ac(2))+'/'+str(msg.v_ac(3))+' Volts')
        # Send p_ac(1-3)
        if (msg.p_ac(1)<99999 and self.config.has_option(section_id, 'AC1_power_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC1_power_idx'): msg.p_ac(1),
            })
        else: self.logger.debug('AC1 power out of range, or not defined: '+str(msg.p_ac(1))+' Watt')
        if (msg.p_ac(2)<99999 and self.config.has_option(section_id, 'AC2_power_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC2_power_idx'): msg.p_ac(2),
            })
        else: self.logger.debug('AC2 power out of range, or not defined: '+str(msg.p_ac(2))+' Watt')
        if (msg.p_ac(3)<99999 and self.config.has_option(section_id, 'AC3_power_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC3_power_idx'): msg.p_ac(3),
            })
        else: self.logger.debug('AC3 power out of range, or not defined: '+str(msg.p_ac(3))+' Watt')
        if (self.config.has_option(section_id, 'AC123_power_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC123_power_idx'): p_ac_t,
            })
        else: self.logger.debug('AC123 power not defined: '+str(p_ac_t)+' Watt')
        # Send f_ac(1-3)
        if (mf<msg.f_ac(1)<70 and self.config.has_option(section_id, 'AC1_frequency_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC1_frequency_idx'): msg.f_ac(1),
            })
        else: self.logger.debug('AC1 frequency out of range, or not defined: '+str(msg.f_ac(1))+' Hertz')
        if (mf<msg.f_ac(2)<70 and self.config.has_option(section_id, 'AC2_frequency_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC2_frequency_idx'): msg.f_ac(2),
            })
        else: self.logger.debug('AC2 frequency out of range, or not defined: '+str(msg.f_ac(2))+' Hertz')
        if (mf<msg.f_ac(3)<70 and self.config.has_option(section_id, 'AC3_frequency_idx')):
            data_idx_array.update ({
                self.config.get(section_id, 'AC3_frequency_idx'): msg.f_ac(3),
            })
        else: self.logger.debug('AC3 frequency out of range, or not defined: '+str(msg.f_ac(3))+' Hertz')

        for idx, value in list(data_idx_array.items()):
            get_data = {
                'svalue': value,
                'type': 'command',
                'param': 'udevice',
                'idx' : idx,
                'nvalue': '0'
                }

            if sys.version[:1] == '2':
                get_data_encoded = urllib.urlencode(get_data)
                self.logger.debug(url + '?' + get_data_encoded)
                request_object = urllib2.Request(url + '?' + get_data_encoded)
                try:
                    response = urllib2.urlopen(request_object)
                except urllib2.HTTPError as e:
                    self.logger.error('HTTP error : '+str(e.code)+' Reason: '+str(e.reason))
                    return []
                except urllib2.URLError as e:
                    self.logger.error('URL error : '+str(e.args)+' Reason: '+str(e.reason))
                    return []
                else:
                    self.logger.debug(response.read())  # Show the response
            else:
                get_data_encoded = urllib.parse.urlencode(get_data)
                self.logger.debug(url + '?' + get_data_encoded)
                request_object = urllib.request.Request(url + '?' + get_data_encoded)
                try:
                    response = urllib.request.urlopen(request_object)
                except urllib.error.HTTPError as e:
                    self.logger.error('HTTP error : '+str(e.code)+' Reason: '+str(e.reason))
                    return []
                except urllib.error.URLError as e:
                    self.logger.error('URL error : '+str(e.args)+' Reason: '+str(e.reason))
                    return []
                else:
                    self.logger.debug(response.read())  # Show the response
