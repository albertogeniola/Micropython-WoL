ARG UBUNTU_VER=22.04
FROM ubuntu:UBUNTU_VER

ENV MP_TAG=v1.22.2
ENV IDF_VER=v5.0.4

# Install base env
RUN apt-get update && apt-get install -y build-essential libffi-dev git pkg-config wget python3 python3-dev python3-pip python3-venv cmake

# Add the entrypoint
COPY --chmod=755 entrypoint.sh /entrypoint.sh
WORKDIR /tmp

ENTRYPOINT [ "/entrypoint.sh", "$MP_TAG", "$IDF_VER" ]