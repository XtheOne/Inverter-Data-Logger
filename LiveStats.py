#!/usr/bin/python
"""OmnikExport LiveStats

Get data from the omniksol inverter and output to console. This is a small
utility program that just changes the config to output anything to console.
"""
import OmnikExport


if __name__ == "__main__":
    omnik_exporter = OmnikExport.OmnikExport('config.cfg')

    omnik_exporter.override_config('general', 'enabled_plugins',
                                   'ConsoleOutput')
    omnik_exporter.override_config('log', 'type', 'console')
    omnik_exporter.override_config('log', 'level', 'debug')
    omnik_exporter.run()
