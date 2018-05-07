import PluginLoader
import sys

class ConsoleOutput(PluginLoader.Plugin):
    """Outputs the data from the inverter logger to stdout"""

    def process_message(self, msg):
        """Output the information from the inverter to stdout.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """
        sys.stdout.write('Inverter ID: {0}\n'.format(msg.id))

        sys.stdout.write('E Today : {0:>5}   Total: {1:<5}\n'.format(msg.e_today, ((((msg.e_today*10)-(int(msg.e_today*10)))/10)+msg.e_total)))
        sys.stdout.write('H Total : {0:>5}   Temp : {1:<5}\n'.format(msg.h_total, msg.temp))
        sys.stdout.write('errorMsg: {0:>5}\n'.format(msg.errorMsg))

        sys.stdout.write('PV1   V: {0:>5}   I: {1:>4}\n'.format(msg.v_pv(1), msg.i_pv(1)))
        sys.stdout.write('PV2   V: {0:>5}   I: {1:>4}\n'.format(msg.v_pv(2), msg.i_pv(2)))
        sys.stdout.write('PV3   V: {0:>5}   I: {1:>4}\n'.format(msg.v_pv(3), msg.i_pv(3)))

        sys.stdout.write('L1    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}\n'.format(msg.p_ac(1), msg.v_ac(1), msg.i_ac(1), msg.f_ac(1)))
        sys.stdout.write('L2    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}\n'.format(msg.p_ac(2), msg.v_ac(2), msg.i_ac(2), msg.f_ac(2)))
        sys.stdout.write('L3    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}\n'.format(msg.p_ac(3), msg.v_ac(3), msg.i_ac(3), msg.f_ac(3)))
