# ESP32
python -m esptool -p COM5 -b 460800 --chip esp32 write_flash 0x10000 built/build-ESP32_GENERIC/micropython.bin
