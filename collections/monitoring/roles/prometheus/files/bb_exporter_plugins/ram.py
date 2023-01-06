# RAM load plugin for bb exporter
# 2020 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
# https://github.com/bluebanquise/bluebanquise - MIT license

import psutil
from prometheus_client.core import GaugeMetricFamily


class Collector(object):

    def __init__(self, empty):
        pass

    def collect(self):
        g = GaugeMetricFamily('system_ram_load_bytes', 'System RAM load in bytes, from psutil')
        ram_load = psutil.virtual_memory()[2]
        print('RAM collector. RAM load: '+str(ram_load))
        g.add_metric(['ram_load'], ram_load)
        yield g
