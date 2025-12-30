#!/bin/bash

# . CONFIG.sh

# set -o xtrace       ## To debug scripts
# set -o errexit      ## To exit on error
# set -o errunset     ## To exit if a variable is referenced but not set


function main() {
    _STARGET="${1}"
    _SPATH="${HOME}/.config/solarfm/plugins/youtube_download"
    LINK=`xclip -selection clipboard -o`

    cd "${_SPATH}"
    echo "Working Dir: " $(pwd)
    
    rm "${_SPATH}/../../cookies.txt"

    # Note: Export cookies to file 
    python "${_SPATH}/yt_dlp/__main__.py" \
            --cookies-from-browser firefox --cookies "${_SPATH}/../../cookies.txt"

    # Note: Use cookies from browser directly
    # python "${_SPATH}/yt_dlp/__main__.py" \
    #         --cookies-from-browser firefox --write-sub --embed-sub --sub-langs en \
    #         -o "${_STARGET}/%(title)s.%(ext)s" "${LINK}"

    # Note:  Download video
    python "${_SPATH}/yt_dlp/__main__.py" \
            -f "bestvideo[height<=1080][ext=mp4][vcodec^=av]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
            --cookies "${_SPATH}/../../cookies.txt" --write-sub --embed-sub --sub-langs en \
            -o "${_STARGET}/%(title)s.%(ext)s" "${LINK}"

}
main "$@";