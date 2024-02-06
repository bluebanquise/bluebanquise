#!/bin/bash

for dev in "$@"
  do
    if [ -d /sys/block/${dev} ] ; then
      echo deadline > /sys/block/${dev}/queue/scheduler
      echo 256 > /sys/block/${dev}/queue/nr_requests
      echo 4096 > /sys/block/${dev}/queue/read_ahead_kb
      echo 1280 > /sys/block/${dev}/queue/max_sectors_kb
      echo 0 > /sys/block/${dev}/queue/nomerges
      echo 1 > /sys/block/${dev}/queue/rq_affinity
    fi
  done
