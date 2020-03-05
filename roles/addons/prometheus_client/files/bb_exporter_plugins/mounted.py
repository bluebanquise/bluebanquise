# Mounted point plugin for bb exporter
# 2020 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
# https://github.com/bluebanquise/bluebanquise - MIT license

import os.path
from prometheus_client.core import GaugeMetricFamily


class Collector(object):

    mounted_points = {}

    def __init__(self, parameters):
        self.mounted_points = parameters
        print('Mounted points exporter. To watch:')
        for point_to_check in self.mounted_points:
            print('  - '+point_to_check)

    def collect(self):
        gauge_mounted_points = GaugeMetricFamily('system_mounted_points_state', 'System mounted points', labels=['path'])

        for point_to_check in self.mounted_points:
            result = os.path.ismount(point_to_check)
            if result:  # result is True
                print('Mounted collector. Point '+point_to_check+' state: Mounted')
                gauge_mounted_points.add_metric([point_to_check], 1.0)
            else:
                print('Mounted collector. Point '+point_to_check+' state: Not Mounted')
                gauge_mounted_points.add_metric([point_to_check], 0.0)
        yield gauge_mounted_points
