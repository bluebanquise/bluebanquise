#!/usr/bin/env bash
# rm -f /tmp/RHEL_in.sh
eval $(which cp) -f RHEL_in.sh /tmp
#for distrib in "almalinux:9"
for distrib in "almalinux:8" "rockylinux:8" "almalinux:9" "rockylinux:9"
do
#    sudo rm -Rf /tmp/image
    echo $distrib
    docker rmi $distrib
    # Priviledged is mandatory for EL9 builds
    docker run --rm --privileged -v /tmp:/tmp $distrib /tmp/RHEL_in.sh $distrib
done

# End up with images in /tmp like:
# AlmaLinux_8.8_minimal_x86_64.tar.gz
# AlmaLinux_9.2_minimal_x86_64.tar.gz
# Rocky_Linux_8.8_minimal_x86_64.tar.gz

