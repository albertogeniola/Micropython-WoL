import gc
import json

_HEX_DIGITS = "0123456789ABCDEF"


class WolDevice:
    def __init__(self, mac: str, name: str, ip: str = None):
        self.mac = mac
        self.name = name
        self.ip = ip

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, value: str):
        normalized = value.upper().replace(":", "-").strip()
        tokens = normalized.split("-")
        if len(tokens) != 6:
            raise ValueError("Invalid mac address specified")
        for hexchars in tokens:
            if len(hexchars) != 2:
                raise ValueError("Invalid mac address specified")
            for hexchar in hexchars:
                if hexchar not in _HEX_DIGITS:
                    raise ValueError("Invalid mac address specified")
        self._mac = normalized

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value: str):
        self._ip = value

    def to_dict(self):
        return {
            "name": self.name,
            "mac": self.mac,
            "ip": self.ip
        }

    @classmethod
    def from_dict(cls, data):
        return WolDevice(name=data["name"], mac=data["mac"], ip=data.get("ip"))


class DeviceRegistry:
    def __init__(self):
        self._devices = {}

    def get_devices(self):
        return self._devices

    def add_update_device(self, name, mac, ip):
        d = WolDevice(mac=mac, name=name, ip=ip)
        self._devices[d.mac] = d
        self.persist()
        return d

    def delete_device(self, mac):
        if mac not in self._devices:
            raise ValueError("Invalid or unregistered device with that mac")
        del self._devices[mac]
        self.persist()

    def persist(self):
        with open("devices.json", "wb", encoding="utf8") as f:
            json.dump({k: v.to_dict() for (k, v) in self._devices.items()}, f)
        gc.collect()

    def load(self):
        with open("devices.json", "rb", encoding="utf8") as f:
            self._devices = {k: WolDevice.from_dict(v) for (k, v) in json.load(f).items()}
        gc.collect()

_dev_registry = DeviceRegistry()
