import PluginLoader


class ConsoleOutput(PluginLoader.Plugin):
    """Outputs the data from the Omnik inverter to stdout"""

    def process_message(self, msg):
        """Output the information from the inverter to stdout.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """
        print "ID: {0}".format(msg.id)

        print "E Today: {0:>5}   Total: {1:<5}".format(msg.e_today, msg.e_total)
        print "H Total: {0:>5}   Temp:  {1:<5}"\
            .format(msg.h_total, msg.temperature)

        print "PV1   V: {0:>5}   I: {1:>4}".format(msg.v_pv(1), msg.i_pv(1))
        print "PV2   V: {0:>5}   I: {1:>4}".format(msg.v_pv(2), msg.i_pv(2))
        print "PV3   V: {0:>5}   I: {1:>4}".format(msg.v_pv(3), msg.i_pv(3))

        print "L1    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
            .format(msg.p_ac(1), msg.v_ac(1), msg.i_ac(1), msg.f_ac(1))
        print "L2    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
            .format(msg.p_ac(2), msg.v_ac(2), msg.i_ac(2), msg.f_ac(2))
        print "L3    P: {0:>5}   V: {1:>5}   I: {2:>4}   F: {3:>5}"\
            .format(msg.p_ac(3), msg.v_ac(3), msg.i_ac(3), msg.f_ac(3))
