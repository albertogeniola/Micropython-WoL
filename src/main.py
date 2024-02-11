import machine
import time
from controller import _controller
from hardware_initializer import init as hardware_init, hw

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
