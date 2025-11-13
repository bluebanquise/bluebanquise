CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if (( $STEP < 2 )); then

    echo " 02 Start http server."
    echo "   - Grabing isos"
    cd $CURRENT_DIR/../http
    wget -nc https://releases.ubuntu.com/22.04/ubuntu-22.04.1-live-server-amd64.iso
    #wget -nc https://releases.ubuntu.com/20.04/ubuntu-20.04.5-live-server-amd64.iso
    echo "   - Extracting boot files"
    sudo mkdir -p /bbmnt
    ! mountpoint -q /bbmnt || sudo umount /bbmnt
    sudo mount ubuntu-22.04.1-live-server-amd64.iso /bbmnt
    cp -a /bbmnt/casper/initrd . && chmod 666 initrd
    cp -a /bbmnt/casper/vmlinuz . && chmod 666 vmlinuz
    (
    set -x
    cd $CURRENT_DIR/../http
    ps -ax | grep 'python3 -m http.server 8000'
#    if [ $? -eq 1 ]; then
       python3 -m http.server 8000 > http_server.log 2>&1
#    fi
    ) &
    export http_server_pid=$!
    echo "  - http server pid: $http_server_pid"
fi
