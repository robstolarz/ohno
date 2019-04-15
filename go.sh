#!/bin/bash
mkdir -p build/{originals,crops}
# TODO: 2to3 tumblr-utils
python2 ./tumblr-utils/tumblr_backup.py -O ./build/originals --no-reblog --incremental webcomicname
# TODO: this sucks, can we cache it in a way that doesn't suck
find ./build/originals/media -type f -exec ./ohnoify.py '{}' -o ./build/crops \;
