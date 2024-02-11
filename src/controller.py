import gc
import time
from os import remove as fremove

import machine
import json
import wifi
from configuration import _configuration
from constants import OPMODE_NOT_CONFIGURED, OPMODE_CONFIGURED, OPMODE_CONFIGURING, DEBUG, DEFAULT_ESSID, DEFAULT_PASSWORD, DEFAULT_HOSTNAME, RESET_TIMER
from device import _dev_registry
from exceptions import InvalidConfiguration
from futils import fexists
from hardware_initializer import hw

try:
    import ubluetooth
    BLUETOOTH_SUPPORTED = True
except:
    print("Bluetooth is unsupported on this board.")
    BLUETOOTH_SUPPORTED = False

_LED = machine.Pin(2, mode=machine.Pin.OUT)
_RESET = machine.Pin(0, mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)


def _blink(*args, **kwargs):
    _LED.value(not _LED.value())


def adv_encode(adv_type, value):
    return bytes((len(value) + 1, adv_type,)) + value


def adv_encode_name(name):
    return adv_encode(0x09, name.encode())


def _advertise_ble(ip):
    if not BLUETOOTH_SUPPORTED:
        return
    ble = ubluetooth.BLE()
    ble.active(True)
    ble.gap_advertise(62500, adv_data=adv_encode_name(f'ESP32-WoL {ip}'))


def _run_configured():
    while True:
        wifi_config = wifi.connect(ssid=_configuration.ssid, ssid_password=_configuration.ssid_password,
                                   hostname=DEFAULT_HOSTNAME, network_config=_configuration.get_network_config())
        if wifi_config is not None:
            break
    gc.collect()
    _advertise_ble(wifi_config[0])
    gc.collect()
    from web_configured import app
    hw.display.set_configured(_configuration.ssid, wifi_config[0])
    app.run(debug=DEBUG, host=wifi_config[0], port=80)


def _run_configuration():
    gc.collect()
    hw.display.set_configuring(ssid=_configuration.ssid)
    wifi_config = wifi.connect(ssid=_configuration.ssid, ssid_password=_configuration.ssid_password, 
                               hostname=DEFAULT_HOSTNAME, network_config=_configuration.get_network_config())
    if wifi_config is None:
        _configuration.error = "Cannot connect to specified wifi"
        _configuration.save_to_file("error.json")
        return
    print("Configuration was successful. Persisting to config file...")
    _configuration.error = None
    _configuration.save_to_file("config.json")
    print("Configuration saved.")
    if fexists("install.json"):
        fremove("install.json")
    if fexists("error.json"):
        fremove("error.json")
    machine.reset()


def _run_unconfigured():
    # TODO: set error?
    # Perform initial scanning
    hw.display.notify_scan_started()
    from web_unconfigured import scanned_networks
    scanned_networks.clear()
    scanned_networks.extend([x.to_dict() for x in wifi.scan(configure_station=True)])
    hw.display.notify_scan_over()
    essid, password, wifi_config = wifi.set_ap(DEFAULT_ESSID, DEFAULT_PASSWORD, DEFAULT_HOSTNAME)
    hw.display.set_unconfigured(essid, password, wifi_config[0])
    gc.collect()
    from web_unconfigured import app
    app.run(debug=DEBUG, host=wifi_config[0], port=80)


class OperationModeController:
    def __init__(self):
        self._mode = OPMODE_NOT_CONFIGURED
        self._blink_timer = None
        self._reset_timer = None
        self._timer_start_time = None

    def _attempt_load(self, filename):
        if fexists(filename):
            try:
                _configuration.load_from_file(filename)
                return True
            except InvalidConfiguration as e:
                print("Missing or invalid configuration file. Skipping.")
        return False
    
    def load_configuration(self):
        # Load config.json and run, if config.json exists
        if self._attempt_load("config.json"):
            self.set_mode(OPMODE_CONFIGURED)
        elif self._attempt_load("error.json"):
            self.set_mode(OPMODE_NOT_CONFIGURED)
        elif self._attempt_load("install.json"):
            self.set_mode(OPMODE_CONFIGURING)
        else:
            self.set_mode(OPMODE_NOT_CONFIGURED)
        return self._mode

    def run(self):
        gc.enable()
        if self._mode == OPMODE_CONFIGURED:
            print("Configuration file loaded successfully.")
            _run_configured()
            return
        elif self._mode == OPMODE_CONFIGURING:
            print("Found installation file, configuring.")
            _run_configuration()
            return
        else:
            print("The device is not yet configured.")
            _run_unconfigured()
            return

    def _stop_blink_timer(self):
        if self._blink_timer is not None:
            self._blink_timer.deinit()
            self._blink_timer = None

    def _set_blink_timer(self, period):
        self._blink_timer = machine.Timer(-1)
        self._blink_timer.init(mode=machine.Timer.PERIODIC, period=period, callback=_blink)

    def _set_led_mode(self, mode):
        # Mode 0, not configured = Blink slowly
        # Mode 1, applying configuration = Blink quickly
        # Mode 2, configured = Fixed ON
        if mode == OPMODE_NOT_CONFIGURED:
            self._stop_blink_timer()
            self._set_blink_timer(1000)
        elif mode == OPMODE_CONFIGURING:
            self._stop_blink_timer()
            self._set_blink_timer(200)
        elif mode == OPMODE_CONFIGURED:
            self._stop_blink_timer()
            _LED.value(1)

    def _reset_long_press(self, *args, **kwargs):
        now = time.time()
        print(f"Checking timer. NOW={now}, START={self._timer_start_time}. Button Status={_RESET.value()}")
        if _RESET.value() == 1:
            print("Reset button released.")
            # Clean timer
            self._timer_start_time = -1
            if self._reset_timer is not None:
                self._reset_timer.deinit()
                self._reset_timer = None
        elif (now - self._timer_start_time) >= 5:  # 5 seconds reset timer
            print("Issuing reset!")
            if fexists("install.json"):
                fremove("install.json")
            if fexists("error.json"):
                fremove("error.json")
            if fexists("config.json"):
                fremove("config.json")
            # Clean timer
            self._timer_start_time = -1
            self._reset_timer.deinit()
            self._reset_timer = None
            # Reset
            machine.reset()

    def _reset_handler(self, pin):
        print(f"Button pressed: {pin}")
        if pin != _RESET:
            return

        # Button has been re-pressed. Start over again.
        if self._reset_timer is not None:
            self._reset_timer.deinit()
        self._timer_start_time = time.time()
        self._reset_timer = machine.Timer(RESET_TIMER)
        self._reset_timer.init(mode=machine.Timer.PERIODIC, period=500, callback=self._reset_long_press)

    def _set_reset_handler(self):
        _RESET.irq(trigger=machine.Pin.IRQ_FALLING, handler=self._reset_handler)

    @property
    def current_mode(self):
        return self._mode

    def set_mode(self, value):
        self._mode = value
        self._set_reset_handler()
        self._set_led_mode(value)

        if self._mode == OPMODE_CONFIGURED:
            try:
                _dev_registry.load()
            except Exception as e:
                print(f"Unable to load devices, error: {str(e)}")


_controller = OperationModeController()
