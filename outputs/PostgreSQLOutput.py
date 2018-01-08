import PluginLoader
import datetime
import logging

class PostgreSQLOutput(PluginLoader.Plugin):
    def process_message(self, msg):
        import psycopg2

        with psycopg2.connect(self.config.get('postgresql', 'connstr')) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO inverter_reading (
                    inverter, timestamp, kwh_total, kwh_today, inverter_temperature, inverter_hours,
                    pv1_voltage, pv2_voltage, pv3_voltage,
                    pv1_current, pv2_current, pv3_current,
                    ac1_voltage, ac2_voltage, ac3_voltage,
                    ac1_current, ac2_current, ac3_current,
                    ac1_frequency, ac2_frequency, ac3_frequency,
                    ac1_power, ac2_power, ac3_power)
                VALUES (
                    %s, now(), %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                );
                """, (
                    msg.id, msg.e_total, msg.e_today, msg.temperature, msg.h_total,
                    msg.v_pv(1), msg.v_pv(2), msg.v_pv(3),
                    msg.i_pv(1), msg.i_pv(2), msg.i_pv(3),
                    msg.v_ac(1), msg.v_ac(2), msg.v_ac(3),
                    msg.i_ac(1), msg.i_ac(2), msg.i_ac(3),
                    msg.f_ac(1), msg.f_ac(2), msg.f_ac(3),
                    msg.p_ac(1), msg.p_ac(2), msg.p_ac(3)
                    ))
