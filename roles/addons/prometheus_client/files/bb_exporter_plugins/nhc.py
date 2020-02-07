# CPU usage plugin for bb exporter
# 2020 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
# https://github.com/oxedions/bluebanquise - MIT license

import subprocess
import sys
from prometheus_client.core import GaugeMetricFamily


class Collector(object):
    def __init__(self, empty):
        pass

    def collect(self):
        try:
            retcode = subprocess.call("nhc", shell=True)
            if retcode < 0:
                print("Child was terminated by signal", -retcode, file=sys.stderr)
            else:
                print("Child returned", retcode, file=sys.stderr)
        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)
        g = GaugeMetricFamily("system_nhc_status", 'Node Health Checker exit code')
        print('NHC collector. retcode = '+str(retcode))
        g.add_metric(["nhc_exit_code"], retcode)
        yield g
