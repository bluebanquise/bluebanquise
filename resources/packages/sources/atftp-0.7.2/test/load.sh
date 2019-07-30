#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: load.sh [host] [port]"
    exit 1
fi

TFTP=../atftp
HOST=$1
PORT=$2
FILE=linux
CONCURENT=40
TIMEOUT=80
LOOP=1
i=$LOOP
while [ $i -gt 0 ]; do
    echo -n "Loop $i "
    j=$CONCURENT
    while [ $j -gt 0 ]; do
	$TFTP --tftp-timeout 5 --timeout 10 --get -r $FILE -l /dev/null $HOST $PORT 2>$j.out&
	echo -n "."
	j=$[ $j - 1 ]
    done
    echo  " done"
    i=$[ $i - 1 ]
    if [ $i -gt 0 ]; then
  	sleep $TIMEOUT
    fi
done
