import PluginLoader
import datetime


class MysqlOutput(PluginLoader.Plugin):
    """Stores the data from the Omnik inverter into a mysql database"""

    def process_message(self, msg):
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
                        (msg.getID(), datetime.datetime.now(), msg.getETotal(),
                         msg.getEToday(), msg.getTemp(), msg.getHTotal(),
                         msg.getVPV(1),
                         msg.getVPV(2), msg.getVPV(3), msg.getIPV(1),
                         msg.getIPV(2),
                         msg.getIPV(3), msg.getVAC(1), msg.getVAC(2),
                         msg.getVAC(3),
                         msg.getIAC(1), msg.getIAC(2), msg.getIAC(3),
                         msg.getFAC(1),
                         msg.getFAC(2), msg.getFAC(3), msg.getPAC(1),
                         msg.getPAC(2),
                         msg.getPAC(3)))
