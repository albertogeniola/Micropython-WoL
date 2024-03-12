#!/bin/bash
if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters, expected MP_TAG and IDF_VER"
    exit 1
fi

# Print info
MP_TAG=$1
IDF_VER=$2
echo "MP_TAG=$MP_TAG"
echo "IDF_VER=$IDF_VER"

# Clone the latest microptyhon version
git clone https://github.com/micropython/micropython 
cd micropython
git checkout tags/$MP_TAG

# Build mypy
cd mpy-cross && cd /tmp

# Install necessary libs for building ESP32
pip3 install pyelftools
git clone --depth 1 --branch $IDF_VER https://github.com/espressif/esp-idf.git
git -C esp-idf submodule update --init --recursive
./esp-idf/install.sh

# Load the IDF builder
. ./esp-idf/export.sh

# Copy the submodules before building
# TODO

# Build the ESP32_GENERIC port
cd /tmp/micropython/ports/esp32
make submodules
make BOARD=ESP32_GENERIC
make BOARD=ESP32_GENERIC_S2
make BOARD=ESP32_GENERIC_S3
make ports/esp32 BOARD=ESP32_GENERIC_C3

# Copy the submodules before building
# TODO: prepare the artifacts