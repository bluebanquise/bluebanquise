#! /bin/sh
#
# atftpd - Script to launch atftpd server.
#
### BEGIN INIT INFO
# Provides:          atftpd
# Required-Start:    $syslog $network $remote_fs
# Required-Stop:     $syslog $network $remote_fs
# Should-Start:      $local_fs
# Should-Stop:       $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Launch atftpd server
# Description:       Launch atftpd server, a TFTP server useful
#                    for network boot (PXE).
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/sbin/atftpd
NAME=atftpd
DESC="Advanced TFTP server"
USE_INETD=true
OPTIONS=""

test -f $DAEMON || exit 0

set -e

if [ -f /etc/default/atftpd ]; then
    . /etc/default/atftpd
fi

if [ "$USE_INETD" = "true" ]; then
    exit 0;
fi

# Make sure we have --daemon when not using inetd
echo "$OPTIONS"|grep -q -- --daemon || OPTIONS="--daemon $OPTIONS"

case "$1" in
  start)
	echo -n "Starting $DESC: "
	start-stop-daemon --start --oknodo --quiet --exec $DAEMON -- $OPTIONS
	echo "$NAME."
	;;
  stop)
	echo -n "Stopping $DESC: "
	start-stop-daemon --stop --oknodo --quiet --exec $DAEMON
	echo "$NAME."
	;;
  restart|reload|force-reload)
	echo -n "Restarting $DESC: "
	start-stop-daemon --stop --oknodo --quiet --exec $DAEMON
	sleep 1
	start-stop-daemon --start --oknodo --quiet --exec $DAEMON -- $OPTIONS
	echo "$NAME."
	;;
  *)
	N=/etc/init.d/$NAME
        echo "Usage: $N {start|stop|restart|reload|force-reload}" >&2
	exit 1
	;;
esac

exit 0
