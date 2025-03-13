# Services plugin for bb exporter
# 2020 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
# https://github.com/bluebanquise/bluebanquise - MIT license

from pystemd.systemd1 import Unit
from prometheus_client.core import GaugeMetricFamily


class Collector(object):

    services = {}
    services_status = []

    def __init__(self, parameters):
        self.services = parameters
        print('Services collector. Loading services status:')
        for idx, service in enumerate(self.services):
            print('  - Loading '+service)
            self.services_status.append(Unit(service, _autoload=True))
            print(self.services_status)

    def collect(self):
        gauge_services = GaugeMetricFamily('system_services_state', 'System services status', labels=['service'])

        for idx, service in enumerate(self.services):
            result = self.services_status[idx].Unit.SubState
            if 'running' in str(result):
                print('Services collector. Service '+service+' is running.')
                gauge_services.add_metric([service], 1.0)
            else:
                print('Services collector. Service '+service+' is stopped.')
                gauge_services.add_metric([service], 0.0)

        yield gauge_services
