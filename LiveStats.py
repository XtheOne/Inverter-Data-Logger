#!/usr/bin/python
"""InverterExport LiveStats

Get data from the inverter logger and output to console. This is a small
utility program that just changes the config to output anything to console.
"""
import InverterExport


if __name__ == "__main__":
    inverter_exporter = InverterExport.InverterExport('config.cfg')

    inverter_exporter.override_config('general', 'enabled_plugins',
                                   'ConsoleOutput')
    inverter_exporter.override_config('log', 'type', 'console')
    inverter_exporter.override_config('log', 'level', 'debug')
    inverter_exporter.run()
