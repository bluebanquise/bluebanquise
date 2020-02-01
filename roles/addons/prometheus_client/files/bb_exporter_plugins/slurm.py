# Slurm plugin for bb exporter
# To export sinfo metrics, not slurmd or slurmctld daemons. If you need to watch these, use services plugin.
# 2020 - Benoît Leveugle <benoit.leveugle@sphenisc.com>
# https://github.com/oxedions/bluebanquise - MIT license

import time
import subprocess
import sys
from prometheus_client.core import GaugeMetricFamily, REGISTRY

class collector(object):
    def __init__(self,empty):
        pass

    def collect(self):
        gauge_nodes_states_total = GaugeMetricFamily('slurm_nodes_state_total', 'Slurm nodes states, total per state. From sinfo.', labels=['state'])

        # Gather down nodes, and exclude unknown status nodes (down*)
        try:
            stdout,stderr = subprocess.Popen("sinfo --format='%T %D' | grep down | grep -v '*' |awk -F ' ' '{print $2}'", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()
            try:
                nb_nodes_down = float(stdout)
            except ValueError:
                nb_nodes_down = 0.0
            print("Slurm Exporter. nb_nodes_down: "+str(nb_nodes_down))
            gauge_nodes_states_total.add_metric(["down"], nb_nodes_down)
        except OSError as e:
            print("Execution failed:", e, file=stderr)

#        try:
#            nb_nodes_down = subprocess.call("sinfo --format='%T %D' | grep down | grep -v '*' |awk -F ' ' '{print $2}'", shell=True)
#            if nb_nodes_down < 0:
#                print("Child was terminated by signal", -nb_nodes_down, file=sys.stderr)
#            else:
#                print("Child returned", nb_nodes_down, file=sys.stderr)
#                gauge_nodes_states_total.add_metric(["down"], nb_nodes_down)
#        except OSError as e:
#            print("Execution failed:", e, file=sys.stderr)

        # Gather drain nodes, and exclude unknown status nodes (drain*)
        try:
            stdout,stderr = subprocess.Popen("sinfo --format='%T %D' | grep drain | grep -v '*' |awk -F ' ' '{print $2}'", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()
            try:
                nb_nodes_drain = float(stdout)
            except ValueError:
                nb_nodes_drain = 0.0
            print("Slurm Exporter. nb_nodes_drain: "+str(nb_nodes_drain))
            gauge_nodes_states_total.add_metric(["drain"], nb_nodes_drain)
        except OSError as e:
            print("Execution failed:", e, file=stderr)

        # Gather idle nodes, and exclude unknown status nodes (idle*)
        try:
            stdout,stderr = subprocess.Popen("sinfo --format='%T %D' | grep idle | grep -v '*' |awk -F ' ' '{print $2}'", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()
            try:
                nb_nodes_idle = float(stdout)
            except ValueError:
                nb_nodes_idle = 0.0
            print("Slurm Exporter. nb_nodes_idle: "+str(nb_nodes_idle))
            gauge_nodes_states_total.add_metric(["idle"], nb_nodes_idle)
        except OSError as e:
            print("Execution failed:", e, file=stderr)

        # Gather alloc nodes, and exclude unknown status nodes (alloc*)
        try:
            stdout,stderr = subprocess.Popen("sinfo --format='%T %D' | grep alloc | grep -v '*' |awk -F ' ' '{print $2}'", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()
            try:
                nb_nodes_alloc = float(stdout)
            except ValueError:
                nb_nodes_alloc = 0.0
            print("Slurm Exporter. nb_nodes_alloc: "+str(nb_nodes_alloc))
            gauge_nodes_states_total.add_metric(["alloc"], nb_nodes_alloc)
        except OSError as e:
            print("Execution failed:", e, file=stderr)

        # Deduce remaining nodes, and assume they are unknown state
        try:
            stdout,stderr = subprocess.Popen("sinfo --format=%D | grep -v NODES", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()
            try:
                nb_nodes = float(stdout)
            except ValueError:
                nb_nodes = 0.0
            print("Slurm Exporter. nb_nodes: "+str(nb_nodes))
            gauge_nodes_states_total.add_metric(["unk"], nb_nodes-(nb_nodes_alloc+nb_nodes_idle+nb_nodes_drain+nb_nodes_down))
        except OSError as e:
            print("Execution failed:", e, file=stderr)

        yield gauge_nodes_states_total

