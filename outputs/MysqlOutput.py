import PluginLoader
import datetime


class MysqlOutput(PluginLoader.Plugin):
    """Stores the data from the Omnik inverter into a mysql database"""

    def process_message(self, msg):
        """Store the information from the inverter in a mysql database.

        Args:
            msg (InverterMsg.InverterMsg): Message to process
        """
        import MySQLdb

        self.logger.debug('Connect to database')
        con = MySQLdb.connect(self.config.get('mysql', 'host'),
                              self.config.get('mysql', 'user'),
                              self.config.get('mysql', 'pass'),
                              self.config.get('mysql', 'database'))

        with con:
            cur = con.cursor()
            self.logger.debug('Executing SQL statement on database')
            cur.execute("""INSERT INTO minutes
            (InvID, timestamp, ETotal, EToday, Temp, HTotal, VPV1, VPV2, VPV3,
             IPV1, IPV2, IPV3, VAC1, VAC2, VAC3, IAC1, IAC2, IAC3, FAC1, FAC2,
             FAC3, PAC1, PAC2, PAC3)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s);""",
                        (msg.id, datetime.datetime.now(), msg.e_total,
                         msg.e_today, msg.temperature, msg.h_total,
                         msg.v_pv(1), msg.v_pv(2), msg.v_pv(3),
                         msg.i_pv(1), msg.i_pv(2), msg.i_pv(3),
                         msg.v_ac(1), msg.v_ac(2), msg.v_ac(3),
                         msg.i_ac(1), msg.i_ac(2), msg.i_ac(3),
                         msg.f_ac(1), msg.f_ac(2), msg.f_ac(3),
                         msg.p_ac(1), msg.p_ac(2), msg.p_ac(3)
                         ))
