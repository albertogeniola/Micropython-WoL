import time
import gc
import network


class ScannedWifi:
    def __init__(self, ssid, bssid, channel, rssi, security, hidden) -> None:
        self.ssid = ssid
        self.bssid = bssid
        self.channel = channel
        self.rssi = rssi
        self.security = security
        self.hidden = hidden

    def is_open(self):
        return self.security == 0
    
    def to_dict(self):
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "channel": self.channel,
            "rssi": self.rssi,
            "security": self.security,
            "hidden": self.hidden
        }


def set_ap(essid, password, hostname):
    gc.collect()
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_if.config(essid=essid, password=password, authmode=network.AUTH_WPA_WPA2_PSK, dhcp_hostname=hostname)
    while not ap_if.active():
        time.sleep(0.1)
    return essid, password, ap_if.ifconfig()


def connect(ssid, ssid_password, hostname, network_config=None, wifi_attempt_timeout=15.0):
    station = network.WLAN(network.STA_IF)
    station.active(False)
    time.sleep(0.5)
    station.active(True)
    ssid = ssid
    password = ssid_password
    print(f"Attempting the connection to: {ssid}")
    timeout = time.time() + wifi_attempt_timeout
    if network_config is not None:
        if len(network_config) != 4:
            raise Exception("Bad network configuration")
        station.ifconfig(network_config)
    station.config(dhcp_hostname=hostname)
    station.connect(ssid, password)

    # Wait up to timeout
    while not station.isconnected() and time.time() < timeout:
        pass

    if not station.isconnected():
        print(f"Could not connect to {ssid} in {wifi_attempt_timeout} seconds.")
        return None

    config = station.ifconfig()
    print(f"Connection successful: {config}")
    return config


def scan(configure_station=False):
    # Note! This method needs to be invoked while the AP is in STATION mode. 
    ap_if = network.WLAN(network.STA_IF)
    if configure_station:
        ap_if.active(True)
        while not ap_if.active():
            time.sleep(0.1)
    if not ap_if.active():
        print("Scanning won't proceed as WIFI is not in STATION mode.")
        return []
    res = []
    for net in ap_if.scan():
        bssid_hex = bytes(net[1],"utf-8").hex()
        res.append(ScannedWifi(
            ssid=net[0].decode("utf8"),
            bssid=":".join([bssid_hex[0:2],bssid_hex[2:4],bssid_hex[4:6],bssid_hex[6:8],bssid_hex[8:10],bssid_hex[10:12]]),
            channel=net[2],
            rssi=net[3],
            security=net[4],
            hidden=net[5]==1))
        print(f"Found network: {net[0]}")
    return res