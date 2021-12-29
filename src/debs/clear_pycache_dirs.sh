#!/bin/bash

# set -o xtrace       ## To debug scripts
# set -o errexit      ## To exit on error
# set -o errunset     ## To exit if a variable is referenced but not set


function main() {
    find . -name "__pycache__" -exec rm -rf $1 {} \;
    find . -name "*.pyc" -exec rm -rf $1 {} \;
}
main
