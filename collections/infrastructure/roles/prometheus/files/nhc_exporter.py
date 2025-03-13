# This is a minimal exporter, to be used as a reference.

import time
import subprocess
import sys
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server


class CustomCollector(object):
    def __init__(self):
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
        g = GaugeMetricFamily("nhc", 'Node Health Checker')
        g.add_metric(["nhc_exit_code"], retcode)
        yield g


if __name__ == '__main__':
    start_http_server(8777)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
