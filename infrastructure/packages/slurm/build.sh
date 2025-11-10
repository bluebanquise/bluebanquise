set -x
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source $CURRENT_DIR/version.sh
source $CURRENT_DIR/../common.sh

###### MUNGE

# Munge only needs to be built on RHEL systems, it is provided by all other distributions in native repos.
if [ $distribution != "Ubuntu" ] && [ $distribution != "opensuse_leap" ] && [ $distribution != "Debian" ]; then

    package_version=$munge_version
    package_name=munge
    package_path_calc

    if [ ! -f $package_path ]; then

        if [ ! -f $working_directory/sources/munge-$munge_version.tar.xz ]; then
            wget -P $working_directory/sources/ https://github.com/dun/munge/releases/download/munge-$munge_version/munge-$munge_version.tar.xz
        fi

        if [ ! -f $working_directory/sources/dun.gpg ]; then
            wget -P $working_directory/sources/ https://github.com/dun.gpg
        fi

        if [ ! -f $working_directory/sources/munge-$munge_version.tar.xz.asc ]; then
            wget -P $working_directory/sources/ https://github.com/dun/munge/releases/download/munge-$munge_version/munge-$munge_version.tar.xz.asc
        fi

        rm -Rf $working_directory/build/munge
        mkdir -p $working_directory/build/munge
        cd $working_directory/build/munge
        cp $working_directory/sources/munge-$munge_version.tar.xz $working_directory/build/munge/
        cp $working_directory/sources/dun.gpg $working_directory/build/munge/dun.gpg
        cp $working_directory/sources/munge-$munge_version.tar.xz.asc $working_directory/build/munge/munge-$munge_version.tar.xz.asc
        tar xvJf munge-0.5.16.tar.xz
        sed -i 's/%if 0%{?fedora} < 36/%if (0%{?rhel} \&\& 0%{?rhel} < 10) || (0%{?fedora} \&\& 0%{?fedora} < 36)/' munge-0.5.16/munge.spec
        tar cJvf munge-0.5.16.tar.xz munge-0.5.16
        # rm -f /root/rpmbuild/RPMS/$distribution_architecture/munge*
        rpmbuild -ta munge-$munge_version.tar.xz

    fi
fi

###### SLURM

# Since 23.11, it is possible to build slurm packages natively with deb mechanism.

package_version=$slurm_version
package_name=slurm
if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
package_name=slurm-smd
fi
package_path_calc

if [ ! -f $package_path ]; then

    if [ $distribution != "Ubuntu" ] && [ $distribution != "opensuse_leap" ] && [ $distribution != "Debian" ]; then
        # We need to install munge to build slurm on RHEL
        dnf install /root/rpmbuild/RPMS/$distribution_architecture/munge* -y
    fi

    if [ ! -f $working_directory/sources/slurm-$slurm_version.tar.bz2 ]; then
        wget -P $working_directory/sources/ https://download.schedmd.com/slurm/slurm-$slurm_version.tar.bz2
    fi

    rm -Rf $working_directory/build/slurm
    mkdir -p $working_directory/build/slurm
    cd $working_directory/build/slurm
    cp  $working_directory/sources/slurm-$slurm_version.tar.bz2 $working_directory/build/slurm
    #        tar xjvf slurm-$slurm_version.tar.bz2
    #        sed -i '1s/^/%global _hardened_ldflags\ "-Wl,-z,lazy"\n/' slurm-$slurm_version/slurm.spec
    #        sed -i '1s/^/%global _hardened_cflags\ "-Wl,-z,lazy"\n/' slurm-$slurm_version/slurm.spec
    #        sed -i '1s/^/%undefine\ _hardened_build\n/' slurm-$slurm_version/slurm.spec
    #        sed -i 's/BuildRequires:\ python/#BuildRequires:\ python/g' slurm-$slurm_version/slurm.spec
    #        tar cjvf slurm-$slurm_version.tar.bz2 slurm-$slurm_version
    if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
        tar xjvf slurm-$slurm_version.tar.bz2
        cd slurm-$slurm_version
        mk-build-deps -i debian/control
        if [ $distribution_architecture == 'arm64' ]; then
            if [ $distribution == "Debian" ]; then
                sed -i 's/--with-pmix/--with-pmix=\/usr\/lib\/aarch64-linux-gnu\/pmix2\//' debian/rules
            fi
            if [ $distribution == "Ubuntu" ]; then
                if [ "$distribution_version" == "24.04" ] || [ "$distribution_version" == "22.04" ]; then
                    sed -i 's/--with-pmix/--with-pmix=\/usr\/lib\/aarch64-linux-gnu\/pmix2\//' debian/rules
                else
                    sed -i 's/--with-pmix/--with-pmix=\/usr\/lib\/aarch64-linux-gnu\/pmix\//' debian/rules
                fi
            fi
        fi
        debuild -b -uc -us
        cd ../
        mkdir -p /root/debbuild/DEBS/$distribution_architecture/
        mv *.deb /root/debbuild/DEBS/$distribution_architecture/
        # sed -i 's|%{!?_unitdir|#%{!?_unitdir|' slurm-$slurm_version/slurm.spec
        # sed -i '1s|^|%define\ _unitdir\ /etc/systemd/system\n|' slurm-$slurm_version/slurm.spec
        # sed -i 's|BuildRequires:\ systemd|#BuildRequires:\ systemd|' slurm-$slurm_version/slurm.spec
        # sed -i 's|BuildRequires:\ munge-devel|#BuildRequires:\ munge-devel|' slurm-$slurm_version/slurm.spec
        # sed -i 's|BuildRequires:\ python3|#BuildRequires:\ python3|' slurm-$slurm_version/slurm.spec
        # sed -i 's|BuildRequires:\ readline-devel|#BuildRequires:\ readline-devel|' slurm-$slurm_version/slurm.spec
        # sed -i 's|BuildRequires:\ perl(ExtUtils::MakeMaker)|#BuildRequires:\ perl(ExtUtils::MakeMaker)|' slurm-$slurm_version/slurm.spec
        # # sed -i 's|BuildRequires:\ mariadb-devel|#BuildRequires:\ mariadb-devel|' slurm-$slurm_version/slurm.spec
        # sed -i 's|BuildRequires:\ pam-devel|#BuildRequires:\ pam-devel|' slurm-$slurm_version/slurm.spec
        # sed -i 's|%{_perlman3dir}/Slurm*|#%{_perlman3dir}/Slurm*|' slurm-$slurm_version/slurm.spec
        # sed -i '1s/^/%define _build_id_links none\n/' slurm-$slurm_version/slurm.spec
        # tar cjvf slurm-$slurm_version.tar.bz2 slurm-$slurm_version
    else

    # if [ $distribution == "opensuse_leap" ]; then
    #     tar xjvf slurm-$slurm_version.tar.bz2
    #     # Package on sles is libmariadb-devel
    #     sed -i 's|BuildRequires:\ mariadb-devel|#BuildRequires:\ mariadb-devel|' slurm-$slurm_version/slurm.spec
    #     tar cjvf slurm-$slurm_version.tar.bz2 slurm-$slurm_version
    # fi

        rpmbuild -ta --target=$distribution_architecture slurm-$slurm_version.tar.bz2
    fi

    # if [ $distribution == "Ubuntu" ] || [ $distribution == "Debian" ]; then
    #     cd /root
    #     alien --to-deb /root/rpmbuild/RPMS/$distribution_architecture/slurm*
    #     mkdir -p /root/debbuild/DEBS/$distribution_architecture/
    #     mv *.deb /root/debbuild/DEBS/$distribution_architecture/
    # fi

fi
