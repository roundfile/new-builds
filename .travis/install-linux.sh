#!/bin/sh

set -ex
sudo apt-get update -y -q
sudo apt-get install -y -q ruby-dev build-essential p7zip-full rpm gdb libudev-dev qt5-default
#sudo apt-get install -y -q fakeroot

# add libs not installed by default on Qt5.15 any longer
sudo apt-get install -y -q libdbus-1-3 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0

gem install fpm
pip install --upgrade pip
pip install -r src/requirements.txt
pip install -r src/requirements-${ARTISAN_OS}.txt

.travis/install-libusb.sh
.travis/install-phidgets.sh
.travis/install-snap7.sh
