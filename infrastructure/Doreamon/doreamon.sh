#!/bin/bash
export PATH=$HOME/.local/bin:$PATH
CURRENT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -x
set -e
python3 -m venv $HOME/pvenv
source $HOME/pvenv/bin/activate
pip3 install --upgrade sphinx sphinx-book-theme mkdocs mkdocs-material
export PATH=$HOME/.local/bin:$PATH

# Prepare html
mkdir -p $HOME/website
cp index.html $HOME/website/

# Grab credentials
source $HOME/credentials.sh

# Prepare gits
mkdir -p gits
cd gits
git clone https://github.com/bluebanquise/bluebanquise.git || echo "repo already exists"
git clone https://github.com/bluebanquise/infrastructure.git || echo "repo already exists"
git clone https://github.com/bluebanquise/website.git || echo "repo already exists"
cd ../


set_status () {
 return 0
  # CSS buttons
  bsuccess='\<a class=\"button is-success\"\> Success \<\/a\>'
  berror='\<a class=\"button is-danger\"\> Error \<\/a\>'
  bwaiting='\<a class=\"button is-info\"\> Waiting \<\/a\>'
  brunning='\<a class=\"button is-primary is-loading\"\> Running \<\/a\>'
  bspace='\&nbsp\;\&nbsp\;'
  btable_pre='                \<td\>'
  btable_app='<\/td\>'

  target=$1
  if [[ "$2" == "error" ]]; then
    status="$berror"
  elif [[ "$2" == "success" ]]; then
    status=$bsuccess
  elif [[ "$2" == "waiting" ]]; then
    status=$bwaiting
  elif [[ "$2" == "running" ]]; then
    status=$brunning
  elif [[ "$2" == "date" ]]; then
    status=$(date)
  else
    status=$2
  fi
  # if $3 == 0 then table
  if [[ $3 == 0 ]]; then
  sudo sed -i "s/^.*<\!--$target-->.*$/$btable_pre$status$btable_app<\!--$target-->/" $HOME/website/index.html
  else
  sudo sed -i "s/^.*<\!--$target-->.*$/$bspace$status<\!--$target-->/" $HOME/website/index.html
  fi

#  sshpass -p "$website_pass" sftp $website_user@ftp.$website_host <<EOF
#put $HOME/website/index.html /home/$website_user/bluebanquise/infrastructure/index.html
#exit
#EOF

}

set_status_debug () {
  # CSS buttons
  bsuccess='\<a class=\"button is-success\"\> Success \<\/a\>'
  berror='\<a class=\"button is-danger\"\> Error \<\/a\>'
  bwaiting='\<a class=\"button is-info\"\> Waiting \<\/a\>'
  brunning='\<a class=\"button is-primary is-loading\"\> Running \<\/a\>'
  bspace='\&nbsp\;\&nbsp\;'
  btable_pre='                \<td\>'
  btable_app='<\/td\>'

  target=$1
  if [[ "$2" == "error" ]]; then
    status="$berror"
  elif [[ "$2" == "success" ]]; then
    status=$bsuccess
  elif [[ "$2" == "waiting" ]]; then
    status=$bwaiting
  elif [[ "$2" == "running" ]]; then
    status=$brunning
  elif [[ "$2" == "date" ]]; then
    status=$(date)
  else
    status=$2
  fi
  # if $3 0 then table, 1 is 2 spaces
  if [[ $3 == 0 ]]; then
  cat index.html | sed "s/^.*<\!--$target-->.*$/$btable_pre$status$btable_app<\!--$target-->/"
  elif [[ $3 == 1 ]]; then
  cat index.html | sed "s/^.*<\!--$target-->.*$/$bspace$status<\!--$target-->/"
  fi
}


# Main loop
while [ 1 ]
do

    gits_bluebanquise_update=0
    gits_website_update=0
    gits_infrastructure_update=0
    gits_diskless_update=0
    disable_diskless_update=0

    tag_bluebanquise="NA"
    tag_infrastructure="NA"
    tag_website="NA"

    # Check if any updates
    echo "[Gits] Starting check..."
    cd $CURRENT_DIR/gits/bluebanquise

    git remote update
    UPSTREAM=${1:-'@{u}'}
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse "$UPSTREAM")
    BASE=$(git merge-base @ "$UPSTREAM")

    if [ $LOCAL = $REMOTE ]; then
        echo "[Gits] BlueBanquise Up-to-date"
    elif [ $LOCAL = $BASE ]; then
        echo "[Gits] BlueBanquise Need to pull"
        git pull
        gits_bluebanquise_update=1
    elif [ $REMOTE = $BASE ]; then
        echo "[Gits] BlueBanquise Need to push"
    else
        echo "[Gits] BlueBanquise Diverged !"
    fi

    tag_bluebanquise=$(git describe --tags)
    set_status bluebanquise_tag ${tag_bluebanquise} 1

    cd $CURRENT_DIR/gits/infrastructure
    git remote update
    UPSTREAM=${1:-'@{u}'}
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse "$UPSTREAM")
    BASE=$(git merge-base @ "$UPSTREAM")

    if [ $LOCAL = $REMOTE ]; then
        echo "[Gits] Infrastructure Up-to-date"
    elif [ $LOCAL = $BASE ]; then
        echo "[Gits] Infrastructure Need to pull"
        git pull
        gits_infrastructure_update=1
    elif [ $REMOTE = $BASE ]; then
        echo "[Gits] Infrastructure Need to push"
    else
        echo "[Gits] Infrastructure Diverged !"
    fi

    tag_infrastructure=$(git log --format="%H" -n 1)
    set_status infrastructure_tag ${tag_infrastructure} 1

    cd $CURRENT_DIR/gits/website
    git remote update
    UPSTREAM=${1:-'@{u}'}
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse "$UPSTREAM")
    BASE=$(git merge-base @ "$UPSTREAM")

    if [ $LOCAL = $REMOTE ]; then
        echo "[Gits] Website Up-to-date"
    elif [ $LOCAL = $BASE ]; then
        echo "[Gits] Website Need to pull"
        git pull
        gits_website_update=1
    elif [ $REMOTE = $BASE ]; then
        echo "[Gits] Website Need to push"
    else
        echo "[Gits] Website Diverged !"
    fi

    tag_website=$(git log --format="%H" -n 1)
    set_status website_tag ${tag_website} 1

    cd $CURRENT_DIR
    echo "[Gits] Done."

    # Check if manual build requested
    if test -f "gits_bluebanquise_update"; then
        gits_bluebanquise_update=1
	rm -f gits_bluebanquise_update
    fi
    if test -f "gits_website_update"; then
        gits_website_update=1
        rm -f gits_website_update
    fi
    if test -f "gits_infrastructure_update"; then
        gits_infrastructure_update=1
        rm -f gits_infrastructure_update
    fi
    if test -f "gits_no_infrastructure_update"; then
        gits_infrastructure_update=0
        rm -f gits_no_infrastructure_update
    fi
    if test -f "gits_diskless_update"; then
        gits_diskless_update=1
        rm -f gits_diskless_update
    fi
    if test -f "disable_diskless_update"; then
        disable_diskless_update=1
    fi

    if [ "$gits_website_update" -eq 1 ]; then

        echo "[Website] Starting website upload"
        set_status web running 1
        set_status web_last_attempt date 1
        (
            set -x
            set -e
            rm -Rf /dev/shm/website
            cp -a gits/website /dev/shm
            rm -Rf /dev/shm/website/.git
            rm -f /dev/shm/website/.gitignore
            rm -Rf /dev/shm/website/.git*
            sshpass -p "$website_pass" sftp $website_user@ftp.$website_host <<EOF
put -r /dev/shm/website/bluebanquise/* /home/$website_user/bluebanquise/
exit
EOF
        )
        if [ $? -eq 0 ]; then
            echo "[Website] Done."
            echo "[Website] Forcing main bluebanquise refresh now."
            set_status web success 1
            set_status web_last_success date 1
            gits_bluebanquise_update=1
        else
            echo "[Website] ERROR."
            set_status web error 1
        fi
    fi


    if [ "$gits_bluebanquise_update" -eq 1 ]; then

	cd gits/bluebanquise
	git pull
	cd ../../

        ## MAIN DOC
        echo "[Doc] Starting documentation build"
        set_status doc running 1
        set_status doc_last_attempt date 1
        (
            set -x
            set -e
            rm -Rf /dev/shm/documentation
            cp -a gits/bluebanquise/documentation /dev/shm
            cd /dev/shm/documentation
            make html > /tmp/doreamon_documentation_build_log 2>&1
            echo "[Doc] Uploading documentation"
            lftp -u $website_user,$website_pass sftp://ssh.$website_host <<EOF
rm -r /home/$website_user/bluebanquise/documentation
exit
EOF
            sshpass -p "$website_pass" sftp $website_user@ftp.$website_host <<EOF
mkdir /home/$website_user/bluebanquise/documentation
put -r /dev/shm/documentation/_build/html/* /home/$website_user/bluebanquise/documentation/
exit
EOF
        )
        if [ $? -eq 0 ]; then
            echo "[Doc] Build success !"
            set_status doc success 1
            set_status doc_last_success date 1
        else
            echo "[Doc] Build failed !"
            set_status doc error 1
        fi
        echo "[Doc] Done."
        cd $CURRENT_DIR


        ## TUTORIALS
        echo "[Tuto] Starting tutorials build"
        set_status tuto running 1
        set_status doc_last_attempt date 1
        (
            set -x
            set -e
            rm -Rf /dev/shm/tutorials
            cp -a gits/bluebanquise/tutorials /dev/shm
            cd /dev/shm/tutorials
            mkdocs build > /tmp/doreamon_tutorials_build_log 2>&1
            echo "[Tuto] Uploading Tutorials"
            lftp -u $website_user,$website_pass sftp://ssh.$website_host <<EOF
rm -r /home/$website_user/bluebanquise/tutorials
exit
EOF
            sshpass -p "$website_pass" sftp $website_user@ftp.$website_host <<EOF
mkdir /home/$website_user/bluebanquise/tutorials
put -r /dev/shm/tutorials/site/* /home/$website_user/bluebanquise/tutorials/
exit
EOF
        )
        if [ $? -eq 0 ]; then
            echo "[Tuto] Build success !"
            set_status tuto success 1
            set_status tuto_last_success date 1
        else
            echo "[Tuto] Build failed !"
            set_status tuto error 1
        fi
        echo "[Tuto] Done."
        cd $CURRENT_DIR

    fi

    if [ "$gits_infrastructure_update" -eq 1 ]; then
        echo "[Repo] Starting packages build"
        set_status pr running 1
        set_status pr_last_attempt date 1

        # Set all in waiting
        for os_target in el8 el9 lp15 ubuntu2004 ubuntu2204 ubuntu2404 debian11 debian12; do
            set_status $(echo p_${os_target}_x86_64) waiting 0
            set_status $(echo p_${os_target}_arm64) waiting 0
        done
        set_status upload waiting 1

        # Prepare work
        cd $CURRENT_DIR/gits/infrastructure/CI/
        echo $(date) > /tmp/doreamon_repositories_build_log
        build_was_success="true"
        repo_was_success="true"

        # Loop over os build
        ./engine.sh clean_cache="yes" >> /tmp/doreamon_repositories_build_log 2>&1
        for os_target in el9 el8 lp15 ubuntu2004 ubuntu2204 ubuntu2404 debian11 debian12; do
            set_status $(echo p_${os_target}_x86_64) running 0
            ./engine.sh arch_list="x86_64" os_list="$os_target" steps="build" >> /tmp/doreamon_repositories_build_log 2>&1
            if [ $? -eq 0 ]; then
                set_status $(echo p_${os_target}_x86_64) success 0
            else
                set_status $(echo p_${os_target}_x86_64) error 0
                build_was_success="false"
                break
            fi
            set_status $(echo p_${os_target}_arm64) running 0
            ./engine.sh arch_list="arm64 aarch64" os_list="$os_target" steps="build" >> /tmp/doreamon_repositories_build_log 2>&1
            if [ $? -eq 0 ]; then
                set_status $(echo p_${os_target}_arm64) success 0
            else
                set_status $(echo p_${os_target}_arm64) error 0
                build_was_success="false"
                break
            fi
        done

        # Loop over os repositories build
        if [[ "$build_was_success" == "true" ]]; then
            for os_target in el9 el8 lp15 ubuntu2004 ubuntu2204 ubuntu2404 debian11 debian12; do
                set_status $(echo r_${os_target}_x86_64) running 0
                ./engine.sh arch_list="x86_64" os_list="$os_target" steps="repositories" >> /tmp/doreamon_repositories_build_log 2>&1
                if [ $? -eq 0 ]; then
                    set_status $(echo r_${os_target}_x86_64) success 0
                else
                    set_status $(echo r_${os_target}_x86_64) error 0
                    repo_was_success="false"
                    break
                fi
                set_status $(echo r_${os_target}_arm64) running 0
                ./engine.sh arch_list="arm64 aarch64" os_list="$os_target" steps="repositories" >> /tmp/doreamon_repositories_build_log 2>&1
                if [ $? -eq 0 ]; then
                    set_status $(echo r_${os_target}_arm64) success 0
                else
                    set_status $(echo r_${os_target}_arm64) error 0
                    repo_was_success="false"
                    break
                fi
            done
        fi

	# Make sure repositories will be readable online
	find $HOME/CI/repositories -type f -exec chmod 0644 {} +
	find $HOME/CI/repositories -type d -exec chmod 0755 {} +

        if [[ "$build_was_success" == "true" ]] && [[ "$repo_was_success" == "true" ]]; then
            echo "[Repo] Build success !"
            set_status upload running 1
            (
                set -x
                set -e
                rm -Rf /tmp/distant-repo
                mkdir /tmp/distant-repo
                cp -a $HOME/CI/repositories/* /tmp/distant-repo/
                lftp -u $website_user,$website_pass sftp://ssh.$website_host <<EOF
rm -r /home/$website_user/bluebanquise/repository/releases/latest
exit
EOF
                sshpass -p "$website_pass" sftp $website_user@ftp.$website_host <<EOF
mkdir /home/$website_user/bluebanquise/repository/releases/latest
put -r /tmp/distant-repo/* /home/$website_user/bluebanquise/repository/releases/latest/
exit
EOF
            )
            if [ $? -eq 0 ]; then
                set_status upload success 1
                set_status pr success 1
                set_status pr_last_success date 1
            else
                set_status upload error 1
                set_status pr error 1
            fi
        else
            echo "[Repo] Build failed !"
            set_status pr error 1
        fi
        rm -Rf /tmp/distant-repo
        echo "[Repo] Done."
    fi
    cd $CURRENT_DIR

    if [ "$gits_infrastructure_update" -eq 1 ] || [ "$gits_diskless_update" -eq 1 ]; then
        if [ "$disable_diskless_update" -eq 0 ]; then
            echo "[Diskless] Starting diskless"
            set_status dimages running 1
            set_status dimages_last_attempt date 1
            (
            set -x
            set -e
            cd ../diskless
            ./engine.sh
sshpass -p "$website_pass" sftp $website_user@ftp.$website_host <<EOF
mkdir /home/$website_user/bluebanquise/diskless
put -r /tmp/*x86_64.tar.gz /home/$website_user/bluebanquise/diskless
put -r /tmp/*aarch64.tar.gz /home/$website_user/bluebanquise/diskless
exit
EOF
            ) > /tmp/doreamon_diskless_build_log 2>&1
            if [ $? -eq 0 ]; then
                set_status dimages success 1
                set_status dimages_last_success date 1
            else
                set_status dimages error 1
            fi
            echo "[Diskless] Done."
        fi
    fi
    cd $CURRENT_DIR

    echo "[ALL] Pass done, entering sleep."
    cd $CURRENT_DIR
    sleep 3600
done


