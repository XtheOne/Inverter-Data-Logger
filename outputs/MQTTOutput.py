import PluginLoader
from datetime import datetime
import paho.mqtt.client as mqtt

class MWTTOutput(PluginLoader.Plugin):
        """Outputs the data from the Omnik inverter to an MQTT server """

        def process_message(self, msg):
                client = mqtt.Client("Omnik Solar Inverter")
                client.username_pw_set( self.config.get('mqtt', 'user'),
                                        self.config.get('mqtt', 'pass'))
                client.connect( self.config.get('mqtt', 'host'),
                                self.config.get('mqtt', 'port'))

                client.publish("power/solar/e_total", msg.e_total)
                client.publish("power/solar/e_today", msg.e_today)
                client.publish("power/solar/h_total", msg.h_total)
                client.publish("power/solar/power", msg.power)
                client.publish("power/solar/temp", msg.temperature)

                for x in [1,2,3]:
                        client.publish("power/solar/v_pv" + str(x), msg.v_pv(x))
                        client.publish("power/solar/v_ac" + str(x), msg.v_ac(x))
                        client.publish("power/solar/i_ac" + str(x), msg.i_ac(x))
                        client.publish("power/solar/f_ac" + str(x), msg.f_ac(x))
                        client.publish("power/solar/p_ac" + str(x), msg.p_ac(x))

                client.loop(2)
                client.disconnect()
