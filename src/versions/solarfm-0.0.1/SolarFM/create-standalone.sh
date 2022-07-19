#!/bin/bash

# . CONFIG.sh

# set -o xtrace       ## To debug scripts
# set -o errexit      ## To exit on error
# set -o errunset     ## To exit if a variable is referenced but not set


function main() {
    cd "$(dirname "")"
    echo "Working Dir: " $(pwd)

    source "/home/abaddon/Portable_Apps/py-venvs/gtk-apps-venv/venv/bin/activate"
    python -m nuitka --follow-imports --standalone --linux-onefile-icon="/home/abaddon/.config/solarfm/solarfm.png"  solarfm/__main__.py
}
main "$@";
