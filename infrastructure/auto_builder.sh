#!/bin/bash
# Update before executing
set -x
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
git pull
packages/./build.sh $1 $2 $3 $4
