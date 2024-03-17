ARG UBUNTU_VER=22.04
FROM ubuntu:$UBUNTU_VER

ENV MODULE_SOURCE_PATH=/mnt/source
ENV MODULE_OUTPUT_PATH=/mnt/built
ENV MP_TAG=v1.22.2
ENV IDF_VER=v5.0.4

# Install base env
RUN apt-get update && apt-get install -y build-essential libffi-dev git pkg-config wget python3 python3-dev python3-pip python3-venv cmake libusb-1.0-0-dev autoconf automake libtool gcc g++ gperf flex bison texinfo gawk ncurses-dev libexpat-dev python3-serial sed unzip help2man bzip2 libtool-bin bash unrar-free

# Install necessary libs for building ESP32
WORKDIR /opt
RUN pip3 install pyelftools && \
    git clone --depth 1 --branch $IDF_VER https://github.com/espressif/esp-idf.git && \
    git -C esp-idf submodule update --init --recursive && \
    ./esp-idf/install.sh

# Install necessary libs for building ESP8266
RUN git clone --recursive https://github.com/pfalcon/esp-open-sdk.git && \
    cd esp-open-sdk && \
    make && \
    export PATH=/opt/esp-open-sdk/xtensa-lx106-elf/bin:$PATH

# Add the entrypoint
COPY --chmod=755 entrypoint.sh /entrypoint.sh

WORKDIR /tmp
ENTRYPOINT [ "/entrypoint.sh" ]
CMD "${MODULE_SOURCE_PATH} ${MODULE_OUTPUT_PATH} ${MP_TAG}"