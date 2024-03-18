# ESP8266
python -m esptool --chip esp8266 erase_flash
python -m esptool --chip esp8266 --port COM5 write_flash --flash_mode dio --flash_size detect 0x0 built/build-ESP8266_GENERIC/firmware.bin
