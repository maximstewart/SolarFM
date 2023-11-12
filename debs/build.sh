#!/bin/bash

# Fixes ownershp
function main() {
    sudo find . -type f -exec chmod 644 {} +
    sudo find . -type d -exec chmod 755 {} +

    # Set postrm permissions
    for i in `find . -name postrm`; do
        sudo chmod 755 "${i}"
    done

    # Set pytop permissions
    for i in `find . -name pytop`; do
        sudo chmod 755 "${i}"
    done

    sudo chown -R root:root ./*/

    builder;
    bash ./chownAll.sh
}

#builds debs
function builder() {
    for i in `ls`; do
        if [[ -d "${i}" ]]; then
            dpkg  --build "${i}"
        else
               echo "Not a dir."
        fi
    done
}
main;
