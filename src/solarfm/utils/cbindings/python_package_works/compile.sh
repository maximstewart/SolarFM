#!/bin/bash

# . CONFIG.sh

# set -o xtrace       ## To debug scripts
# set -o errexit      ## To exit on error
# set -o errunset     ## To exit if a variable is referenced but not set

function main() {
    cd "$(dirname "")"
    echo "Working Dir: " $(pwd)

    python3 setup.py build && python3 setup.py install --user
}
main "$@";
