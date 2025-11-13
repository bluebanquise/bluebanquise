set -e
set -x

# Enable QEMU
docker run --privileged --rm tonistiigi/binfmt --install arm64

# Custom docker cache folder
# oxedions@prima:~/gits/infrastructure$ sudo systemctl restart docker
# oxedions@prima:~/gits/infrastructure$ cat /etc/docker/daemon.json 
# {
#         "bip": "172.26.0.1/16",
#         "data-root": "/docker_cache/"
# }
# oxedions@prima:~/gits/infrastructure$

CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Introduce tags, that allows to prevent super long and stupid rebuilds
mkdir -p $HOME/CI/tmp/wd/
mkdir -p $HOME/CI/tmp/cache/

mkdir -p $HOME/CI/tmp/cache/ipxe-arm
mkdir -p $HOME/CI/tmp/cache/ipxe-x86_64
cd $HOME/CI/tmp/cache/
rm -f ipxe-arm64
rm -f ipxe-aarch64
ln -s ipxe-arm ipxe-aarch64
ln -s ipxe-arm ipxe-arm64
cd $CURRENT_DIR

################################################################################
#################### INIT STEP
####

for ARGUMENT in "$@"
do
   KEY=$(echo $ARGUMENT | cut -f1 -d=)

   KEY_LENGTH=${#KEY}
   VALUE="${ARGUMENT:$KEY_LENGTH+1}"

   export "$KEY"="$VALUE"
done

# Clean cache, it was meant to be redone at each build pass
if [ "$clean_cache" == 'yes' ]; then
    rm -Rf $HOME/CI/tmp/cache/*
fi

if [ -z ${packages_list+x} ]; then
    packages_list="all"
    packages_list_for_ipxe=$packages_list
    echo "No packages list passed as argument, will generate all."
else
    echo "Packages list to be generated: $packages_list"
fi

if [ -z ${arch_list+x} ]; then
    arch_list="all"
    echo "No arch list passed as argument, will generate all."
else
    echo "Arch list to be generated: $arch_list"
fi

if [ -z ${os_list+x} ]; then
    os_list="all"
    echo "No os list passed as argument, will generate all."
else
    echo "OS list to be generated: $os_list"
fi

if [ -z ${reset_repos+x} ]; then
    reset_repos="false"
    echo "No repo reset required."
else
    echo "Reset repo: $reset_repos"
fi

if [ -z ${clean_all+x} ]; then
    clean_all="false"
    echo "No clean required."
else
    echo "Clean all: $clean_all"
fi

if [ -z ${steps+x} ]; then
    steps="build repos"
    echo "Will do both build and repositories."
else
    echo "Steps: $steps"
fi

if [ "$clean_build" == 'yes' ]; then
    # Clean builds since it requires sudo, so better ask at the beggining
    sudo rm -Rf $HOME/CI/build
fi

if [ "$clean_all" == 'yes' ]; then
    sudo rm -Rf $HOME/CI/
fi

mkdir -p $HOME/CI/
mkdir -p $HOME/CI/logs/
mkdir -p $HOME/CI/build/{el8,el9,el10,osl15}/{x86_64,aarch64,sources}/
mkdir -p $HOME/CI/build/{u20,u22,u24,deb11,deb12,deb13}/{x86_64,arm64}/
mkdir -p $HOME/CI/repositories/{el8,el9,el10,osl15}/{x86_64,aarch64,sources}/bluebanquise/
mkdir -p $HOME/CI/repositories/{u20,u22,u24,deb11,deb12,deb13}/{x86_64,aarch64}/bluebanquise/
for os in u20 u22 u24 deb11 deb12 deb13; do
   cd $HOME/CI/repositories/$os/
   ln -s aarch64 arm64
done
cd $CURRENT_DIR

rsync -av $CURRENT_DIR/repositories/tree/* $HOME/CI/repositories/

################################################################################
#################### BUILDS
####

if [ "$os_list" == "all" ]; then
    os_list="el9,el8,el10,osl15,u20,u22,u24,deb11,deb12,deb13"
fi

for os_name in $(echo $os_list | sed 's/,/ /g'); do

    # If default request, get packages to be built for this OS
    if [ "$packages_list" == "all" ]; then
        packages_list=$(cat $CURRENT_DIR/build_matrix | grep $os_name | awk -F ' ' '{print $6}')
    fi
    if [ "$arch_list" == "all" ]; then
        archs_list=$(cat $CURRENT_DIR/build_matrix | grep $os_name | awk -F ' ' '{print $2}')
    fi
    os_distribution_name=$(cat $CURRENT_DIR/build_matrix | grep $os_name | awk -F ' ' '{print $3}')
    os_distribution_version_major=$(cat $CURRENT_DIR/build_matrix | grep $os_name | awk -F ' ' '{print $4}')
    os_package_format=$(cat $CURRENT_DIR/build_matrix | grep $os_name | awk -F ' ' '{print $5}')

    if [ "$os_package_format" == "RPM" ]; then
        if [ "$os_distribution_name" == "opensuse_leap" ]; then
            internal_build_path="/usr/src/packages/RPMS/"
        else
            internal_build_path="/root/rpmbuild/RPMS/"
        fi
    else
        internal_build_path="/root/debbuild/DEBS/"
    fi

    #### BUILD
    if echo $steps | grep -q "build"; then
        for cpu_arch in $(echo $archs_list | sed 's/,/ /g'); do

            # For now I build on amd64 CPU, might need to update that later
            if [ "$cpu_arch" == "arm64" ] || [ "$cpu_arch" == "aarch64" ] ; then
                PLATFORM="--platform linux/arm64"
            else
                PLATFORM=""
            fi

            # Check if base image already exists, if not build it
            set +e
            docker images | grep $os_name-build-$cpu_arch
            if [ $? -ne 0 ]; then
                set -e
                docker build $PLATFORM --no-cache --tag $os_name-build-$cpu_arch -f $CURRENT_DIR/build/$os_name/Dockerfile $CURRENT_DIR/build/$os_name/
            fi
            set -e
            # Now build packages
            mkdir -p $HOME/CI/build/$os_name/$cpu_arch/
            for package in $(echo $packages_list | sed 's/,/ /g'); do
                docker run --rm $PLATFORM -v $HOME/CI/build/$os_name/:$internal_build_path -v $HOME/CI/tmp/:/tmp $os_name-build-$cpu_arch $package $os_distribution_name $os_distribution_version_major
            done

        done
    fi

    #### REPOS
    if echo $steps | grep -q "repos"; then

        for cpu_arch in $(echo $archs_list | sed 's/,/ /g'); do

            # For now I build on amd64 CPU, might need to update that later
            if [ "$cpu_arch" == "arm64" ] || [ "$cpu_arch" == "aarch64" ] ; then
                PLATFORM="--platform linux/arm64"
                repo_cpu_arch="aarch64"
            else
                PLATFORM=""
                repo_cpu_arch="x86_64"
            fi

            # Check if base image already exists, if not build it
            set +e
            docker images | grep $os_name-repos-$cpu_arch
            if [ $? -ne 0 ]; then
                set -e
                docker build $PLATFORM --no-cache --tag $os_name-repos-$cpu_arch -f $CURRENT_DIR/build/$os_name/Dockerfile_repos $CURRENT_DIR/build/$os_name/
            fi
            set -e

            # Build repo
            repos_path=$HOME/CI/repositories/$os_name/$repo_cpu_arch/bluebanquise/
            mkdir -p $repos_path
            $(which cp) -af $HOME/CI/build/$os_name/$cpu_arch $repos_path
            $(which cp) -af $HOME/CI/build/$os_name/noarch $repos_path
            source $CURRENT_DIR/build/$os_name/build_repos.sh $repos_path $os_name-repos-$cpu_arch # $reset_repos

        done
    fi

done

set -e
# Last step, scan for security
clamscan -r $HOME/CI/repositories

echo "ALL DONE"
