class Display:
    _configuration_state = 0 # -1: booting, 0: unconfigured, 1: configured, 2: configuring
    _ssid=None
    _password=None
    _ip=None

    def set_booting(self):
        self._configuration_state = -1
        self._draw_booting()

    def set_unconfigured(self, ssid, password, ip):
        self._configuration_state = 0
        self._ssid = ssid
        self._password = password
        self._ip = ip
        self._draw_unconfigured()

    def set_configured(self, ssid, ip):
        self._configuration_state = 1
        self._ssid = ssid
        self._password = None
        self._ip = ip
        self._draw_configured()

    def set_configuring(self, ssid):
        self._configuration_state = 2
        self._ssid = ssid
        self._draw_configuring()

    def _reset_screen(self, *args, **kwargs):
        if self._configuration_state == 0:
            self._draw_unconfigured()
        elif self._configuration_state == 1:
            self._draw_configured()
        elif self._configuration_state == 2:
            self._draw_configuring()

    # Methods to be overridden by sub-classes
    def notify_wol(self, mac, dev_name):
        print(f"!!! Sending magic packet to {mac} ({dev_name}) over LAN broadcast. !!!")

    def notify_scan_started(self):
        print(f"!!! Starting WIFI scanning... !!!")

    def notify_scan_over(self):
        print(f"WIFI scanning completed.")

    def _draw_unconfigured(self):
        print("Ready for first connection.")
        print(f"Connect to {self._ssid} with password {self._password}")
        print(f"Then access http://{self._ip}")

    def _draw_configured(self):
        print("Configuration loaded")
        print(f"Connected to {self._ssid}")
        print(f"Then access http://{self._ip}")

    def _draw_configuring(self):
        print(f"Connecting to {self._ssid}...")

    def _draw_booting(self):
        print(f"ESP32 - WOL Booting up!")
        import os
        info = os.uname()
        print(f"System info:\nsysname={info.sysname}\nnodename={info.nodename}\nrelease={info.release}\nversion={info.version}\nmachine={info.machine}")

        