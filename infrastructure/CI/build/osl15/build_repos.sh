set -x

docker run --rm $PLATFORM -v $1:/repo/ $2 /bin/bash -c ' \
    set -x ; \
    createrepo /repo/ ; \
    '
