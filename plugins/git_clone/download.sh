#!/bin/bash

# . CONFIG.sh

# set -o xtrace       ## To debug scripts
# set -o errexit      ## To exit on error
# set -o errunset     ## To exit if a variable is referenced but not set


function main() {
    cd "$(dirname "")"
    echo "Working Dir: " $(pwd)

    TARGETDIR="${1}"
    LINK=`xclip -selection clipboard -o`

    cd "${TARGETDIR}"
    git clone "${LINK}"
}
main "$@";
