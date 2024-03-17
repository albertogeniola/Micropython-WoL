#!/bin/bash
echo "MODULE_SOURCE_PATH=$MODULE_SOURCE_PATH"
echo "MODULE_OUTPUT_PATH=$MODULE_OUTPUT_PATH"
echo "MP_TAG=$MP_TAG"

pushd /tmp

# Clone the latest microptyhon version
git clone https://github.com/micropython/micropython && \
    pushd micropython && \
    git checkout tags/$MP_TAG && \
    popd

# Load the IDF builder
. /opt/esp-idf/export.sh

# Clean the build directory
rm -R $MODULE_OUTPUT_PATH/*

# Build the ESP32_GENERIC port
# Copy the submodules before building
cp -r $MODULE_SOURCE_PATH/*.py /tmp/micropython/ports/esp32/modules

pushd /tmp/micropython/ports/esp32
make submodules

make BOARD=ESP32_GENERIC
cp -r build-ESP32_GENERIC $MODULE_OUTPUT_PATH

make BOARD=ESP32_GENERIC_S2
cp -r build-ESP32_GENERIC_S2 $MODULE_OUTPUT_PATH

make BOARD=ESP32_GENERIC_C3
cp -r build-ESP32_GENERIC_C3 $MODULE_OUTPUT_PATH
popd

# Build the ESP8266 port
export PATH=$PATH:/opt/xtensa-lx106-elf/bin
cp -r $MODULE_SOURCE_PATH/*.py /tmp/micropython/ports/esp8266/modules
pushd /tmp/micropython
make -C mpy-cross
make -C ports/esp8266 submodules
make -C ports/esp8266 BOARD=ESP8266_GENERIC
#make -C ports/esp8266 BOARD=ESP8266_GENERIC BOARD_VARIANT=FLASH_512K
#make -C ports/esp8266 BOARD=ESP8266_GENERIC BOARD_VARIANT=FLASH_1M
make submodules
cp -r ports/esp8266/build-ESP8266_GENERIC $MODULE_OUTPUT_PATH
#cp -r ports/esp8266/build-ESP8266_GENERIC $MODULE_OUTPUT_PATH
#cp -r ports/esp8266/build-ESP8266_GENERIC $MODULE_OUTPUT_PATH
popd
