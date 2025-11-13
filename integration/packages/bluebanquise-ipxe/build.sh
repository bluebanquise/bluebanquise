set -x

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh


package_ipxe_path_calc() {



    if [ "$distribution" == 'RedHat' ]; then
        if [ $distribution_architecture == 'x86_64' ]; then
            package_distribution_architecture='x86_64'
        elif [ $distribution_architecture == 'arm64' ] || [ $distribution_architecture == 'aarch64' ]; then
            package_distribution_architecture='arm64'
        fi
        package_os_name="el$distribution_version"  # el8, el9, etc
        package_path=/root/rpmbuild/RPMS/noarch/$package_name-$package_distribution_architecture-$package_version.$bluebanquise_ipxe_release-1.noarch.rpm
    elif [ "$distribution" == 'opensuse_leap' ]; then
        if [ $distribution_architecture == 'x86_64' ]; then
            package_distribution_architecture='x86_64'
        elif [ $distribution_architecture == 'arm64' ] || [ $distribution_architecture == 'aarch64' ]; then
            package_distribution_architecture='arm64'
        fi
        package_path=/usr/src/packages/RPMS/noarch/$package_name-$package_distribution_architecture-$package_version.$bluebanquise_ipxe_release-1.noarch.rpm
    elif [ $distribution == 'Ubuntu' ] || [ $distribution == 'Debian' ]; then
        if [ $distribution_architecture == 'x86_64' ]; then
            package_distribution_architecture='x86-64'
        elif [ $distribution_architecture == 'arm64' ] || [ $distribution_architecture == 'aarch64' ]; then
            package_distribution_architecture='arm64'
        fi
        package_path=$(echo "/root/debbuild/DEBS/noarch/$package_name-${package_distribution_architecture}_${package_version}.$bluebanquise_ipxe_release-2_all.deb")
    else
    echo "Error, unknown distribution!"
    exit 1
    fi

    echo "Package path calculated: $package_path"

}

# if [ "$distribution" == 'RedHat' ]; then
#     if [ $distribution_version -eq 7 ]; then
#         if [ $distribution_architecture == 'aarch64' ]; then
#             # scl enable devtoolset-7 bash
#         yum install centos-release-scl -y
#         yum install devtoolset-7 -y
#         set +e
#         source scl_source enable devtoolset-7
#         set -e
#         fi
#     fi
# fi

# iPXE
if [ ! -f $working_directory/sources/ipxe/README ]; then
    mkdir -p $working_directory/sources/ipxe/
    cd $working_directory/sources/ipxe/
    git clone https://github.com/ipxe/ipxe.git .
else
    cd $working_directory/sources/ipxe/
    git pull
fi

if [ -z $bluebanquise_ipxe_release ]
then
    bluebanquise_ipxe_release=$(git rev-list HEAD --count)
fi

if [ $distribution_architecture == 'x86_64' ]; then
    ipxe_arch=x86_64
    debug_flags=intel,dhcp,vesafb
elif [ $distribution_architecture == 'aarch64' ] || [ $distribution_architecture == 'arm64' ]; then
    ipxe_arch=arm64
    debug_flags=intel,dhcp
fi

package_ipxe_path_calc

if [ ! -f $package_path ]; then

    # If cache folder does not exist, create it and build all files
    # If exists, then skip build and package bins directly
    if [ ! -d "$cache_directory/ipxe-$distribution_architecture/bin" ]; then
        mkdir -p $cache_directory/ipxe-$distribution_architecture

        rm -Rf $working_directory/build/ipxe/
        mkdir -p $working_directory/build/ipxe/
        cd $working_directory/build/ipxe/
        cp -a $working_directory/sources/ipxe/* $working_directory/build/ipxe/

        cp $root_directory/bluebanquise-ipxe/grub2-efi-autofind.cfg .
        cp $root_directory/bluebanquise-ipxe/grub2-shell.cfg .

        # Customizing
        # Building embed ipxe files
        last_commit=$(cd $working_directory/sources/ipxe; git log | grep commit | sed -n 1p | awk -F ' ' '{print $2}'; cd ../../../;)

        echo "#!ipxe" > src/bluebanquise_standard.ipxe
        cat $root_directory/bluebanquise-ipxe/$bluebanquise_ipxe_logo.ipxe >> src/bluebanquise_standard.ipxe
        cat $root_directory/bluebanquise-ipxe/bluebanquise_standard.ipxe >> src/bluebanquise_standard.ipxe
        sed -i "s/IPXECOMMIT/$last_commit/" src/bluebanquise_standard.ipxe
        echo "cpair 0" >> src/bluebanquise_standard.ipxe

        echo "#!ipxe" > src/bluebanquise_dhcpretry.ipxe
        cat $root_directory/bluebanquise-ipxe/$bluebanquise_ipxe_logo.ipxe >> src/bluebanquise_dhcpretry.ipxe
        cat $root_directory/bluebanquise-ipxe/bluebanquise_dhcpretry.ipxe >> src/bluebanquise_dhcpretry.ipxe
        sed -i "s/IPXECOMMIT/$last_commit/" src/bluebanquise_dhcpretry.ipxe
        echo "cpair 0" >> src/bluebanquise_dhcpretry.ipxe

        echo "#!ipxe" > src/bluebanquise_allretry.ipxe
        cat $root_directory/bluebanquise-ipxe/$bluebanquise_ipxe_logo.ipxe >> src/bluebanquise_allretry.ipxe
        cat $root_directory/bluebanquise-ipxe/bluebanquise_allretry.ipxe >> src/bluebanquise_allretry.ipxe
        sed -i "s/IPXECOMMIT/$last_commit/" src/bluebanquise_allretry.ipxe
        echo "cpair 0" >> src/bluebanquise_allretry.ipxe

        echo "#!ipxe" > src/bluebanquise_noshell.ipxe
        cat $root_directory/bluebanquise-ipxe/$bluebanquise_ipxe_logo.ipxe >> src/bluebanquise_noshell.ipxe
        cat $root_directory/bluebanquise-ipxe/bluebanquise_noshell.ipxe >> src/bluebanquise_noshell.ipxe
        sed -i "s/IPXECOMMIT/$last_commit/" src/bluebanquise_noshell.ipxe
        echo "cpair 0" >> src/bluebanquise_noshell.ipxe

        cat src/bluebanquise_standard.ipxe
        cat src/bluebanquise_dhcpretry.ipxe
        cat src/bluebanquise_allretry.ipxe
        cat src/bluebanquise_noshell.ipxe

        mkdir $working_directory/build/ipxe/bin/$ipxe_arch/ -p

        if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
            grub-mkstandalone -O $ipxe_arch-efi -o grub2_efi_autofind.img "boot/grub/grub.cfg=grub2-efi-autofind.cfg"
            grub-mkstandalone -O $ipxe_arch-efi -o grub2_shell.img "boot/grub/grub.cfg=grub2-shell.cfg"
        else
            grub2-mkstandalone -O $ipxe_arch-efi -o grub2_efi_autofind.img "boot/grub/grub.cfg=grub2-efi-autofind.cfg"
            grub2-mkstandalone -O $ipxe_arch-efi -o grub2_shell.img "boot/grub/grub.cfg=grub2-shell.cfg"
        fi
        mv grub2_efi_autofind.img $working_directory/build/ipxe/bin/$ipxe_arch/
        mv grub2_shell.img $working_directory/build/ipxe/bin/$ipxe_arch/

        cd src

        # Not sure it worh enabling https without injecting certificates...

        sed -i 's/.*DOWNLOAD_PROTO_HTTPS.*/#define DOWNLOAD_PROTO_HTTPS/' config/general.h
        sed -i 's/.*PING_CMD.*/#define PING_CMD/' config/general.h
        sed -i 's/.*CONSOLE_CMD.*/#define CONSOLE_CMD/' config/general.h
        sed -i 's/.*CONSOLE_FRAMEBUFFER.*/#define CONSOLE_FRAMEBUFFER/' config/console.h
        #sed -i 's/.*IMAGE_BZIMAGE.*/#define IMAGE_BZIMAGE/' config/general.h
        sed -i 's/.*IMAGE_ZLIB.*/#define IMAGE_ZLIB/' config/general.h
        sed -i 's/.*IMAGE_GZIP.*/#define IMAGE_GZIP/' config/general.h
        #sed -i 's/.*IMAGE_EFI.*/#define IMAGE_EFI/' config/general.h
        sed -i 's/.*DIGEST_CMD.*/#define DIGEST_CMD/' config/general.h

        sed -i 's/.*REBOOT_CMD.*/#define REBOOT_CMD/' config/general.h
        sed -i 's/.*POWEROFF_CMD.*/#define POWEROFF_CMD/' config/general.h

        ############################################################################################### STANDARD
        if [ $distribution_architecture == 'x86_64' ]; then
            make -j bin/undionly.kpxe EMBED=bluebanquise_standard.ipxe DEBUG=$debug_flags
        fi
        make -j bin-$ipxe_arch-efi/ipxe.efi EMBED=bluebanquise_standard.ipxe DEBUG=$debug_flags
        make -j bin-$ipxe_arch-efi/snponly.efi EMBED=bluebanquise_standard.ipxe DEBUG=$debug_flags
        make -j bin-$ipxe_arch-efi/snp.efi EMBED=bluebanquise_standard.ipxe DEBUG=$debug_flags
        #        make -j bin/ipxe.iso EMBED=bluebanquise_standard.ipxe DEBUG=$debug_flags
        #        make -j bin/ipxe.usb EMBED=bluebanquise_standard.ipxe DEBUG=$debug_flags

        if [ $distribution_architecture == 'x86_64' ]; then
            rm -Rf /dev/shm/efiiso/efi/boot
            mkdir -p /dev/shm/efiiso/efi/boot
            cp bin-x86_64-efi/ipxe.efi /dev/shm/efiiso/efi/boot/bootx64.efi
            mkisofs -o standard_efi.iso -J -r /dev/shm/efiiso
            cp standard_efi.iso $working_directory/build/ipxe/bin/x86_64/standard_efi.iso
        fi

        mv bin-$ipxe_arch-efi/ipxe.efi $working_directory/build/ipxe/bin/$ipxe_arch/standard_ipxe.efi
        mv bin-$ipxe_arch-efi/snponly.efi $working_directory/build/ipxe/bin/$ipxe_arch/standard_snponly_ipxe.efi
        mv bin-$ipxe_arch-efi/snp.efi $working_directory/build/ipxe/bin/$ipxe_arch/standard_snp_ipxe.efi
        if [ $distribution_architecture == 'x86_64' ]; then
            mv bin/undionly.kpxe $working_directory/build/ipxe/bin/x86_64/standard_undionly.kpxe
        fi
        #        mv bin/ipxe.iso $working_directory/build/ipxe/bin/x86_64/standard_pcbios.iso
        #        mv bin/ipxe.usb $working_directory/build/ipxe/bin/x86_64/standard_pcbios.usb

        ############################################################################################### DHCPRETRY
        if [ $distribution_architecture == 'x86_64' ]; then
            make -j bin/undionly.kpxe EMBED=bluebanquise_dhcpretry.ipxe DEBUG=$debug_flags
        fi
        make -j bin-$ipxe_arch-efi/ipxe.efi EMBED=bluebanquise_dhcpretry.ipxe DEBUG=$debug_flags
        make -j bin-$ipxe_arch-efi/snponly.efi EMBED=bluebanquise_dhcpretry.ipxe DEBUG=$debug_flags
        make -j bin-$ipxe_arch-efi/snp.efi EMBED=bluebanquise_dhcpretry.ipxe DEBUG=$debug_flags
        #        make -j bin/ipxe.iso EMBED=bluebanquise_dhcpretry.ipxe DEBUG=$debug_flags
        #        make -j bin/ipxe.usb EMBED=bluebanquise_dhcpretry.ipxe DEBUG=$debug_flags

        if [ $distribution_architecture == 'x86_64' ]; then
            rm -Rf /dev/shm/efiiso/efi/boot
            mkdir -p /dev/shm/efiiso/efi/boot
            cp bin-x86_64-efi/ipxe.efi /dev/shm/efiiso/efi/boot/bootx64.efi
            mkisofs -o dhcpretry_efi.iso -J -r /dev/shm/efiiso
            cp dhcpretry_efi.iso $working_directory/build/ipxe/bin/x86_64/dhcpretry_efi.iso
        fi

        mv bin-$ipxe_arch-efi/ipxe.efi $working_directory/build/ipxe/bin/$ipxe_arch/dhcpretry_ipxe.efi
        mv bin-$ipxe_arch-efi/snponly.efi $working_directory/build/ipxe/bin/$ipxe_arch/dhcpretry_snponly_ipxe.efi
        mv bin-$ipxe_arch-efi/snp.efi $working_directory/build/ipxe/bin/$ipxe_arch/dhcpretry_snp_ipxe.efi
        if [ $distribution_architecture == 'x86_64' ]; then
            mv bin/undionly.kpxe $working_directory/build/ipxe/bin/x86_64/dhcpretry_undionly.kpxe
        fi
        #        mv bin/ipxe.iso $working_directory/build/ipxe/bin/x86_64/dhcpretry_pcbios.iso
        #        mv bin/ipxe.usb $working_directory/build/ipxe/bin/x86_64/dhcpretry_pcbios.usb

        ############################################################################################### allretry
        if [ $distribution_architecture == 'x86_64' ]; then
            make -j bin/undionly.kpxe EMBED=bluebanquise_allretry.ipxe DEBUG=$debug_flags
        fi
        make -j bin-$ipxe_arch-efi/ipxe.efi EMBED=bluebanquise_allretry.ipxe DEBUG=$debug_flags
        make -j bin-$ipxe_arch-efi/snponly.efi EMBED=bluebanquise_allretry.ipxe DEBUG=$debug_flags
        make -j bin-$ipxe_arch-efi/snp.efi EMBED=bluebanquise_allretry.ipxe DEBUG=$debug_flags
        #        make -j bin/ipxe.iso EMBED=bluebanquise_allretry.ipxe DEBUG=$debug_flags
        #        make -j bin/ipxe.usb EMBED=bluebanquise_allretry.ipxe DEBUG=$debug_flags

        if [ $distribution_architecture == 'x86_64' ]; then
            rm -Rf /dev/shm/efiiso/efi/boot
            mkdir -p /dev/shm/efiiso/efi/boot
            cp bin-x86_64-efi/ipxe.efi /dev/shm/efiiso/efi/boot/bootx64.efi
            mkisofs -o allretry_efi.iso -J -r /dev/shm/efiiso
            cp allretry_efi.iso $working_directory/build/ipxe/bin/x86_64/allretry_efi.iso
        fi

        mv bin-$ipxe_arch-efi/ipxe.efi $working_directory/build/ipxe/bin/$ipxe_arch/allretry_ipxe.efi
        mv bin-$ipxe_arch-efi/snponly.efi $working_directory/build/ipxe/bin/$ipxe_arch/allretry_snponly_ipxe.efi
        mv bin-$ipxe_arch-efi/snp.efi $working_directory/build/ipxe/bin/$ipxe_arch/allretry_snp_ipxe.efi
        if [ $distribution_architecture == 'x86_64' ]; then
            mv bin/undionly.kpxe $working_directory/build/ipxe/bin/x86_64/allretry_undionly.kpxe
        fi
        #        mv bin/ipxe.iso $working_directory/build/ipxe/bin/x86_64/allretry_pcbios.iso
        #        mv bin/ipxe.usb $working_directory/build/ipxe/bin/x86_64/allretry_pcbios.usb

        ############################################################################################### NOSHELL
        if [ $distribution_architecture == 'x86_64' ]; then
            make -j bin/undionly.kpxe EMBED=bluebanquise_noshell.ipxe DEBUG=$debug_flags
        fi
        make -j bin-$ipxe_arch-efi/ipxe.efi EMBED=bluebanquise_noshell.ipxe DEBUG=$debug_flags
        make -j bin-$ipxe_arch-efi/snponly.efi EMBED=bluebanquise_noshell.ipxe DEBUG=$debug_flags
        make -j bin-$ipxe_arch-efi/snp.efi EMBED=bluebanquise_noshell.ipxe DEBUG=$debug_flags
        #        make -j bin/ipxe.iso EMBED=bluebanquise_dhcpretry.ipxe DEBUG=$debug_flags
        #        make -j bin/ipxe.usb EMBED=bluebanquise_dhcpretry.ipxe DEBUG=$debug_flags

        if [ $distribution_architecture == 'x86_64' ]; then
            rm -Rf /dev/shm/efiiso/efi/boot
            mkdir -p /dev/shm/efiiso/efi/boot
            cp bin-x86_64-efi/ipxe.efi /dev/shm/efiiso/efi/boot/bootx64.efi
            mkisofs -o noshell_efi.iso -J -r /dev/shm/efiiso
            cp noshell_efi.iso $working_directory/build/ipxe/bin/x86_64/noshell_efi.iso
        fi

        mv bin-$ipxe_arch-efi/ipxe.efi $working_directory/build/ipxe/bin/$ipxe_arch/noshell_ipxe.efi
        mv bin-$ipxe_arch-efi/snponly.efi $working_directory/build/ipxe/bin/$ipxe_arch/noshell_snponly_ipxe.efi
        mv bin-$ipxe_arch-efi/snp.efi $working_directory/build/ipxe/bin/$ipxe_arch/noshell_snp_ipxe.efi
        if [ $distribution_architecture == 'x86_64' ]; then
            mv bin/undionly.kpxe $working_directory/build/ipxe/bin/x86_64/noshell_undionly.kpxe
        fi
        #        mv bin/ipxe.iso $working_directory/build/ipxe/bin/x86_64/dhcpretry_pcbios.iso
        #        mv bin/ipxe.usb $working_directory/build/ipxe/bin/x86_64/dhcpretry_pcbios.usb

        ###############################################################################################

        cp -a $working_directory/build/ipxe/* $cache_directory/ipxe-$distribution_architecture/

    fi # End of build step
    # From now, files were either fresh built, either we import them from cache

    rm -Rf $working_directory/build/ipxe/
    mkdir -p $working_directory/build/ipxe/
    cp -a $cache_directory/ipxe-$distribution_architecture/* $working_directory/build/ipxe/

    cd $working_directory/build/ipxe/
    bluebanquise_ipxe_version=$package_version
    export bluebanquise_ipxe_version=$bluebanquise_ipxe_version.$bluebanquise_ipxe_release
    mkdir bluebanquise-ipxe-$ipxe_arch-$bluebanquise_ipxe_version
    cp $root_directory/bluebanquise-ipxe/bluebanquise-ipxe-$ipxe_arch.spec bluebanquise-ipxe-$ipxe_arch-$bluebanquise_ipxe_version
    #sed -i "s|Version:\ \ XXX|Version:\ \ $bluebanquise_ipxe_version|g" bluebanquise-ipxe-$ipxe_arch-$bluebanquise_ipxe_version/bluebanquise-ipxe-$ipxe_arch.spec
    sed -i "s|working_directory=XXX|working_directory=$working_directory|g" bluebanquise-ipxe-$ipxe_arch-$bluebanquise_ipxe_version/bluebanquise-ipxe-$ipxe_arch.spec
    tar cvzf bluebanquise-ipxe-$ipxe_arch.tar.gz bluebanquise-ipxe-$ipxe_arch-$bluebanquise_ipxe_version
    if [ "$distribution" == "Ubuntu" ]; then
        if [ "$distribution_version" == "18.04" ]; then
        rpmbuild -ta bluebanquise-ipxe-$ipxe_arch.tar.gz --target=noarch --define "_software_version $bluebanquise_ipxe_version" --define "_software_release 1" --define "dist .ubuntu1804"
        elif [ "$distribution_version" == "20.04" ]; then
        rpmbuild -ta bluebanquise-ipxe-$ipxe_arch.tar.gz --target=noarch --define "_software_version $bluebanquise_ipxe_version" --define "_software_release 1" --define "dist .ubuntu2004"
        elif [ "$distribution_version" == "22.04" ]; then
        rpmbuild -ta bluebanquise-ipxe-$ipxe_arch.tar.gz --target=noarch --define "_software_version $bluebanquise_ipxe_version" --define "_software_release 1" --define "dist .ubuntu2204"
        elif [ "$distribution_version" == "24.04" ]; then
        rpmbuild -ta bluebanquise-ipxe-$ipxe_arch.tar.gz --target=noarch --define "_software_version $bluebanquise_ipxe_version" --define "_software_release 1" --define "dist .ubuntu2404"
        fi
    elif [ "$distribution" == "Debian" ]; then
        if [ "$distribution_version" == "11" ]; then
        rpmbuild -ta bluebanquise-ipxe-$ipxe_arch.tar.gz --target=noarch --define "_software_version $bluebanquise_ipxe_version" --define "_software_release 1" --define "dist .debian11"
        fi
        if [ "$distribution_version" == "12" ]; then
        rpmbuild -ta bluebanquise-ipxe-$ipxe_arch.tar.gz --target=noarch --define "_software_version $bluebanquise_ipxe_version" --define "_software_release 1" --define "dist .debian12"
        fi
        if [ "$distribution_version" == "13" ]; then
        rpmbuild -ta bluebanquise-ipxe-$ipxe_arch.tar.gz --target=noarch --define "_software_version $bluebanquise_ipxe_version" --define "_software_release 1" --define "dist .debian13"
        fi
    else
        rpmbuild -ta bluebanquise-ipxe-$ipxe_arch.tar.gz --target=noarch --define "_software_version $bluebanquise_ipxe_version" --define "_software_release 1"
    fi
    if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
        cd /root
        alien --to-deb --scripts /root/rpmbuild/RPMS/noarch/bluebanquise-ipxe*
        mkdir -p /root/debbuild/DEBS/noarch/
        mv *.deb /root/debbuild/DEBS/noarch/
    fi
fi
