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
    
    # rm "${_SPATH}/../../cookies.txt"

    # Note: Export cookies to file 
    # python "${_SPATH}/yt_dlp/__main__.py" \
    #         --cookies-from-browser firefox --cookies "${_SPATH}/../../cookies.txt"

    python "${_SPATH}/yt_dlp/__main__.py" \
      --js-runtimes deno \
      --cookies-from-browser firefox \
      --concurrent-fragments 8 \
      --embed-metadata \
      --embed-thumbnail \
      --write-auto-subs \
      --sub-langs "en.*" \
      --embed-subs \
      --merge-output-format mp4 \
      --remux-video mp4 \
      -f "bv*[height<=1080]+ba/b[height<=1080]" \
      -o "${_STARGET}/%(title)s.%(ext)s" "${LINK}"
      "${LINK}"


}
main "$@";