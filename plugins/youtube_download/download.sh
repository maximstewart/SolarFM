#!/bin/bash

# . CONFIG.sh

# set -o xtrace       ## To debug scripts
# set -o errexit      ## To exit on error
# set -o errunset     ## To exit if a variable is referenced but not set


function main() {
    cd "$(dirname "")"
    echo "Working Dir: " $(pwd)

    LINK=`xclip -selection clipboard -o`
    yt-dlp --write-sub --embed-sub --sub-langs en -o "${1}/%(title)s.%(ext)s" "${LINK}"
}
main "$@";
