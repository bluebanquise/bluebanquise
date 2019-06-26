#!/bin/bash
#
# This script does some testing with atftp server and client
#
#

# assume we are called in the source tree after the build
# so binaries are one dir up
ATFTP=../atftp
ATFTPD=../atftpd

#
# set some default values for variables used in this script
# if the variables are already set when this script is started
# those values are used
#

: ${HOST:=127.0.0.1}
: ${PORT:=2001}
: ${TEMPDIR:="/tmp"}

# Number of parallel clients for high server load test
: ${NBSERVER:=200}

# Some Tests need root access (e.g. to mount a tempfs filesystem)
# and need sudo for this, so maybe the script asks for a password
#
# if these tests should be performed then start test.sh like this:
#   WANT_INTERACTIVE_TESTS=yes ./test.sh
: ${WANT_INTERACTIVE_TESTS:=no}



#####################################################################################
DIRECTORY=$(mktemp -d ${TEMPDIR}/atftp-test.XXXXXX)

SERVER_ARGS="--daemon --no-fork --logfile=/dev/stdout --port=$PORT --verbose=6 $DIRECTORY"
SERVER_LOG=./atftpd.log

# check if we are root or not root
# if this test is executed by a normal user, atftpd will fail if we do not use our own user+group
if [ ${UID} -ne 0 ]; then
	SERVER_ARGS="--user=$(id -un) --group=$(id -gn) ${SERVER_ARGS}"
fi

ERROR=0

# verify that atftp and atftpd are executable
if [ -x "$ATFTP" ]; then
	echo "Using atftp from build directory"
else
	ATFTP=$(which atftp >/dev/null)
	if [ -x "$ATFTP" ]; then
		echo "Using $ATFTP"
	else
		echo "atftp binary (client) not found - is the PATH setting correct?"
		exit 1
	fi

fi
if [ -x $ATFTPD ]; then
	echo "Using atftpd from build directory"
else
	ATFTPD=$(which atftpd >/dev/null)
	if [ -x "$ATFTPD" ]; then
		echo "Using $ATFTPD"
	else
		echo "atftpd binary (server) not found - is the PATH setting correct?"
		exit 1
	fi
fi

function start_server() {
    # start a server
    echo -n "Starting atftpd server on port $PORT: "
    $ATFTPD  $SERVER_ARGS > $SERVER_LOG &
    if [ $? != 0 ]; then
	echo "Error starting server"
	exit 1
    fi
    sleep 1
    ATFTPD_PID=$!
    # test if server process exists
    ps -p $ATFTPD_PID >/dev/null 2>&1
    if [ $? != 0 ]; then
	echo "server process died"
	exit 1
    fi
    echo "PID $ATFTPD_PID"
}

function stop_server() {
    echo "Stopping atftpd server"
    kill $ATFTPD_PID
}


function check_file() {
    if cmp $1 $2 2>/dev/null ; then
	echo "OK"
    else
	echo "ERROR"
	ERROR=1
    fi
}

function test_get_put() {
    local READFILE="$1"
    shift
    echo -n " get, ${READFILE} ($*)... "
    if [ "$1" = "--option" ]; then
        $ATFTP "$1" "$2" --get --remote-file ${READFILE} --local-file out.bin $HOST $PORT 2>/dev/null
    else
        $ATFTP --get --remote-file ${READFILE} --local-file out.bin $HOST $PORT 2>/dev/null
    fi
    check_file $DIRECTORY/${READFILE} out.bin
    echo -n " put, ${READFILE} ($*)... "
    if [ "$1" = "--option" ]; then
        $ATFTP "$1" "$2" --put --remote-file $WRITE --local-file $DIRECTORY/${READFILE} $HOST $PORT 2>/dev/null
    else
        $ATFTP --put --remote-file $WRITE --local-file $DIRECTORY/${READFILE} $HOST $PORT 2>/dev/null
    fi
    # wait a second
    # because in some case the server may not have time to close the file
    # before the file compare.
    sleep 1
    check_file $DIRECTORY/${READFILE} $DIRECTORY/$WRITE
    rm -f $DIRECTORY/$WRITE out.bin
}

function test_blocksize() {
    echo -n " block size $1 bytes ... "
    $ATFTP --option "blksize $1" --trace --get -r $READ_128K -l /dev/null $HOST $PORT 2> out
    if  [ $(grep DATA out | wc -l) -eq $(( 128*1024 / $1 + 1)) ]; then
	echo "OK"
    else
	echo "ERROR"
	ERROR=1
    fi
}

# make sure we have /tftpboot with some files
if [ ! -d $DIRECTORY ]; then
	echo "create $DIRECTORY before running this test"
	exit 1
fi

# files needed
READ_0=READ_0.bin
READ_511=READ_511.bin
READ_512=READ_512.bin
READ_2K=READ_2K.bin
READ_BIG=READ_BIG.bin
READ_128K=READ_128K.bin
READ_1M=READ_1M.bin
READ_101M=READ_101M.bin
WRITE=write.bin

echo -n "Creating test files ... "
touch $DIRECTORY/$READ_0
touch $DIRECTORY/$WRITE; chmod a+w $DIRECTORY/$WRITE
dd if=/dev/urandom of=$DIRECTORY/$READ_511 bs=1 count=511 2>/dev/null
dd if=/dev/urandom of=$DIRECTORY/$READ_512 bs=1 count=512 2>/dev/null
dd if=/dev/urandom of=$DIRECTORY/$READ_2K bs=1 count=2048 2>/dev/null
dd if=/dev/urandom of=$DIRECTORY/$READ_BIG bs=1 count=51111 2>/dev/null
dd if=/dev/urandom of=$DIRECTORY/$READ_128K bs=1K count=128 2>/dev/null
dd if=/dev/urandom of=$DIRECTORY/$READ_1M bs=1M count=1 2>/dev/null
dd if=/dev/urandom of=$DIRECTORY/$READ_101M bs=1M count=101 2>/dev/null
echo "done"

start_server

#
# test get and put
#
echo "Testng get and put with standard options"
test_get_put $READ_0
test_get_put $READ_511
test_get_put $READ_512
test_get_put $READ_2K
test_get_put $READ_BIG
test_get_put $READ_128K
test_get_put $READ_1M
test_get_put $READ_101M

echo
echo "Testing get and put with misc blocksizes"

test_get_put $READ_BIG --option "blksize 8"
test_get_put $READ_BIG --option "blksize 256"
test_get_put $READ_1M --option "blksize 1428"
test_get_put $READ_1M --option "blksize 1533"
test_get_put $READ_1M --option "blksize 16000"
test_get_put $READ_1M --option "blksize 40000"
test_get_put $READ_1M --option "blksize 65464"

# do not run the following test as it will hang...

#echo
#echo "Testing large file with small blocksize so block numbers will wrap over 65536"
#test_get_put $READ_1M --option "blksize 10"

#
# testing for invalid file name
#
echo
echo -n "Test detection of non-existing file name ... "
$ATFTP --trace --get -r "thisfiledoesntexist" -l /dev/null $HOST $PORT 2> out
if grep -q "<File not found>" out; then
    echo OK
else
    echo ERROR
    ERROR=1
fi

#
# testing for invalid blocksize
# maximum blocksize is 65464 as described in RCF2348
#
echo
echo "Testing blksize option ..."
echo -n " smaller than minimum ... "
$ATFTP --option "blksize 7" --trace --get -r $READ_2K -l /dev/null $HOST $PORT 2> out
if grep -q "<Failure to negotiate RFC1782 options>" out; then
    echo OK
else
    echo ERROR
    ERROR=1
fi
echo -n " bigger than maximum ... "
$ATFTP --option "blksize 65465" --trace --get -r $READ_2K -l /dev/null $HOST $PORT 2> out
if grep -q "<Failure to negotiate RFC1782 options>" out; then
    echo OK
else
    echo ERROR
    ERROR=1
fi


#
# testing for tsize
#
echo ""
echo -n "Testing tsize option... "
$ATFTP --option "tsize" --trace --get -r $READ_2K -l /dev/null $HOST $PORT 2> out
TSIZE=$(grep "OACK <tsize:" out | sed -e "s/[^0-9]//g")
if [ "$TSIZE" != "2048" ]; then
    echo "ERROR (server report $TSIZE bytes but it should be 2048)"
    ERROR=1
else
    echo "OK"
fi

#
# testing for timeout
#
echo ""
echo "Testing timeout option limit..."
echo -n " minimum ... "
$ATFTP --option "timeout 0" --trace --get -r $READ_2K -l /dev/null $HOST $PORT 2> out
if grep -q "<Failure to negotiate RFC1782 options>" out; then
    echo OK
else
    echo ERROR
    ERROR=1
fi
echo -n " maximum ... "
$ATFTP --option "timeout 256" --trace --get -r $READ_2K -l /dev/null $HOST $PORT 2> out
if grep -q "<Failure to negotiate RFC1782 options>" out; then
    echo OK
else
    echo ERROR
    ERROR=1
fi

# Test the behaviour when the server is not reached
# we assume there is no tftp server listening on 127.0.0.77
# Returncode must be 255
echo
echo -n "Test returncode after timeout when server is unreachable ... "
$ATFTP --put --local-file "$DIRECTORY/$READ_2K" 127.0.0.77 2>out
Retval=$?
echo -n "Returncode $Retval: "
if [ $Retval -eq 255 ]; then
	echo "OK"
else
	echo "ERROR"
	ERROR=1
fi

# Test behaviour when disk is full
#
# Preparation: create a small ramdisk
# we need the "sudo" command for that
if [[ $WANT_INTERACTIVE_TESTS = "yes" ]]; then
	echo
	SMALL_FS_DIR="${DIRECTORY}/small_fs"
	echo "Start disk-out-of-space tests, prepare filesystem in ${SMALL_FS_DIR}  ..."
	mkdir "$SMALL_FS_DIR"
	if [[ $(id -u) -eq 0 ]]; then
		Sudo=""
	else
		Sudo="sudo"
		echo "trying to mount ramdisk, the sudo command may ask for a password on the next line!"
	fi
	$Sudo mount -t tmpfs shm "$SMALL_FS_DIR" -o size=500k
	echo "disk space before test: $(LANG=C df -k -P "${SMALL_FS_DIR}" | grep "${SMALL_FS_DIR}" | awk '{print $4}') kiB"
	echo
	echo -n "Put 1M file to server: "
	$ATFTP --put --local-file "$DIRECTORY/$READ_1M" --remote-file "small_fs/fillup.bin" $HOST $PORT
	Retval=$?
	sleep 1
	echo -n "Returncode $Retval: "
	if [ $Retval -ne 0 ]; then
		echo "OK"
	else
		echo "ERROR"
		ERROR=1
	fi
	rm "$DIRECTORY/small_fs/fillup.bin"
	echo
	echo -n "Get 1M file from server: "
	$ATFTP --get --remote-file "$READ_1M" --local-file "$DIRECTORY/small_fs/fillup-put.bin" $HOST $PORT
	Retval=$?
	sleep 1
	echo -n "Returncode $Retval: "
	if [ $Retval -ne 0 ]; then
		echo "OK"
	else
		echo "ERROR"
		ERROR=1
	fi
	$Sudo umount "$SMALL_FS_DIR"
	rmdir "$SMALL_FS_DIR"
else
	echo
	echo "Disk-out-of-space tests not performed, start with \"WANT_INTERACTIVE_TESTS=yes ./test.sh\" if desired." 
fi

# Test that timeout is well set to 1 sec and works.
# we need atftp compiled with debug support to do that
# Restart the server with full logging
if $ATFTP --help 2>&1 | grep --quiet -- --delay
then
    stop_server
    OLD_ARGS="$SERVER_ARGS"
    SERVER_ARGS="$SERVER_ARGS --verbose=7"
    start_server

    $ATFTP --option "timeout 1" --delay 200 --get -r $READ_2K -l /dev/null $HOST $PORT 2> /dev/null &
    CPID=$!
    sleep 1
    kill -s STOP $CPID
    echo -n "Testing timeout "
    for i in $(seq 6); do
	sleep 1
	echo -n "."
    done
    kill $CPID

    stop_server

    sleep 1
    grep "timeout: retrying..." $SERVER_LOG | cut -d " " -f 3 > out
    count=$(wc -l out | cut -d "o" -f1)
    if [ $count != 5 ]; then
	ERROR=1
	echo "ERROR"
    else
	prev=0
	res="OK"
	while read line; do
	    hrs=$(echo $line | cut -d ":" -f 1)
	    min=$(echo $line | cut -d ":" -f 2)
	    sec=$(echo $line | cut -d ":" -f 3)
	    cur=$(( 24*60*10#$hrs + 60*10#$min + 10#$sec ))
	
	    if [ $prev -gt 0 ]; then
		if [ $(($cur - $prev)) != 1 ]; then
		    res="ERROR"
		    ERROR=1
		fi
	    fi
	    prev=$cur
	done < out
	echo " $res"
    fi
    SERVER_ARGS="$OLD_ARGS"
    start_server
else
	echo
	echo "Detailed timeout test could not be done"
	echo "Compile atftp with debug support for more timeout testing"
fi

#
# testing PCRE
#

#
# testing multicast
#

#echo ""
#echo -n "Testing multicast option  "
#for i in $(seq 10); do
#    echo -n "."
#    atftp --blksize=8 --multicast -d --get -r $READ_BIG -l out.$i.bin $HOST $PORT 2> /dev/null&
#done
#echo "OK"

#
# testing mtftp
#


#
# Test for high server load
#
echo
echo "Testing high server load"
echo -n "  starting $NBSERVER simultaneous atftp get processes ... "
#( for i in $(seq 1 $NBSERVER); do
#    ($ATFTP --get --remote-file $READ_1M --local-file /dev/null $HOST $PORT 2> out.$i) &
#    echo -n "+"
#done )
for i in $(seq 1 $NBSERVER)
do
    $ATFTP --get --remote-file $READ_1M --local-file /dev/null $HOST $PORT 2> out.$i &
done
echo "done"
let CHECKCOUNTER=0
let MAXCHECKS=30
while [[ $CHECKCOUNTER -lt $MAXCHECKS ]]; do
    PIDCOUNT=$(pidof $ATFTP|wc -w)
    if [ $PIDCOUNT -gt 0 ]; then
        echo "  wait for atftp processes to complete: $PIDCOUNT running"
        let CHECKCOUNTER+=1
        sleep 1
    else
        let CHECKCOUNTER=$MAXCHECKS+1
    fi
done
error=0;
for i in $(seq 1 $NBSERVER); do
    if grep -q "timeout: retrying..." out.$i; then
	error=1;
    else
        rm out.$i
    fi
done
if [ "$error" -eq "1" ]; then
    echo ERROR;
    ERROR=1
else
    echo OK
fi

stop_server

echo
# cleanup
if [ "$1" == "--nocleanup" ]; then  
    echo "No Cleanup, keep files from test in $DIRECTORY"
else
    echo "Cleanup test files"
    rm -f out
    rm -f $SERVER_LOG $DIRECTORY/$READ_0 $DIRECTORY/$READ_511 $DIRECTORY/$READ_512
    rm -f $DIRECTORY/$READ_2K $DIRECTORY/$READ_BIG $DIRECTORY/$READ_128K $DIRECTORY/$READ_1M
    rm -f $DIRECTORY/$WRITE
    rmdir $DIRECTORY
fi

echo -n "Overall Test status: "
# Exit with proper error status
if [ $ERROR -eq 1 ]; then
    echo "Errors have occurred"
    exit 1
else
    echo "OK"
    exit 0
fi

# vim: ts=4:sw=4:autoindent
