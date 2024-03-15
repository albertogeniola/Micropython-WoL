import machine
import time
from controller import _controller
from hardware_initializer import init as hardware_init, hw

# Handle the static file import 
try:
    import frozen_static
    print("INFO: frozen static folder loaded.")
except:
    import os
    if 'static' not in os.listdir():
        raise("ERROR: frozen_static module not found and no static folder found.")
    print("INFO: found static folder on FS, using it.")


def main():
    print("Starting ESP32 WoL board!")
    hardware_init()
    hw.display.set_booting()
    _controller.load_configuration()
    _controller.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import sys
        sys.print_exception(e)
        time.sleep(2)
        print("Rebooting...")
        machine.reset()
