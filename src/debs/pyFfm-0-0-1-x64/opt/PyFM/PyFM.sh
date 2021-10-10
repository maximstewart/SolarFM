#!/bin/bash

# set -o xtrace       ## To debug scripts
# set -o errexit      ## To exit on error
# set -o errunset     ## To exit if a variable is referenced but not set


function main() {
    # GTK_DEBUG=interactive python3 ./PyFM.py
    python3 ./PyFM.py
}
main $@;
