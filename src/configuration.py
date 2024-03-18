import json

import urandom

from exceptions import InvalidConfiguration
from futils import attempt_load_file

_KEYS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'

def _randrange(start, stop=None):
    if stop is None:
        stop = start
        start = 0
    upper = stop - start
    bits = 0
    pwr2 = 1
    while upper > pwr2:
        pwr2 <<= 1
        bits += 1
    while True:
        r = urandom.getrandbits(bits)
        if r < upper:
            break
    return r + start


def _choice(x):
    return x[_randrange(0, len(x))]

def _generate_secret(length=32):
    return ''.join((_choice(_KEYS) for _ in range(length)))


class Configuration:
    def __init__(self):
        self._error = None
        self._config = {
            "secret": "",
            "network": {
                "ssid": None,
                "password": None,
                "static_ip": None,
                "netmask": None,
                "gateway": None,
                "dns": None
            },
            "users": {}
        }

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        self._error = error

    @property
    def ssid(self):
        return self._config["network"]["ssid"]

    @ssid.setter
    def ssid(self, ssid):
        self._config["network"]["ssid"] = ssid

    @property
    def ssid_password(self):
        return self._config["network"]["password"]

    @ssid_password.setter
    def ssid_password(self, password):
        self._config["network"]["password"] = password

    def get_network_config(self):
        if self.static_ip is None or self.netmask is None or self.gateway is None or self.dns is None:
            return None
        return self.static_ip, self.netmask, self.gateway, self.dns

    @property
    def static_ip(self):
        return self._config["network"]["static_ip"]

    @static_ip.setter
    def static_ip(self, ip):
        self._config["network"]["static_ip"] = ip

    @property
    def netmask(self):
        return self._config["network"]["netmask"]

    @netmask.setter
    def netmask(self, mask):
        self._config["network"]["netmask"] = mask

    @property
    def gateway(self):
        return self._config["network"]["gateway"]

    @gateway.setter
    def gateway(self, gateway):
        self._config["network"]["gateway"] = gateway

    @property
    def dns(self):
        return self._config["network"]["dns"]

    @dns.setter
    def dns(self, dns):
        self._config["network"]["dns"] = dns

    @property
    def admin_password(self):
        return self._config["users"].get("admin")

    @admin_password.setter
    def admin_password(self, password):
        self._config["users"]["admin"] = password

    @property
    def secret(self):
        return self._config["secret"]

    @secret.setter
    def secret(self, secret):
        self._config["secret"] = secret

    def load_from_file(self, fname):
        data = attempt_load_file(fname)
        if data is None:
            raise InvalidConfiguration(f"File {fname} does not exist or contains invalid json")
        self._config = data["config"]
        self._error = data.get("error")

    def save_to_file(self, fname):
        # Everytime we save, generate a new secret
        secret = _generate_secret()
        self._config["secret"] = secret
        print(f"Generated secret: {secret}")
        with open(fname, "wb") as f:
            json.dump({
                "error": self._error,
                "config": self._config
            }, f)


_configuration = Configuration()
