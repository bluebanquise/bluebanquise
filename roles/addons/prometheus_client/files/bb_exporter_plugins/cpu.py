# CPU usage plugin for bb exporter
# 2020 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
# https://github.com/oxedions/bluebanquise - MIT license

import psutil
from prometheus_client.core import GaugeMetricFamily


class Collector(object):

    def __init__(self, empty):
        pass

    def collect(self):
        g = GaugeMetricFamily('system_cpu_load_percent', 'System CPU load in percent, from psutil')
        cpu_load = psutil.cpu_percent()
        print('CPU collector. cpu load: '+str(cpu_load))
        g.add_metric(['cpu_load'], cpu_load)
        yield g
