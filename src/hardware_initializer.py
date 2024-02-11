from futils import fexists
from constants import HW_CONF_FILENAME
import json

from display import Display

class Hardware:
    def __init__(self) -> None:
        self.display = Display()


def init():
    if not fexists(HW_CONF_FILENAME):
        return
    jsondata = None
    try:
        with open(HW_CONF_FILENAME, "rb") as f:
            jsondata = json.load(f)
    except Exception as e:
        print(f"Error while loading {HW_CONF_FILENAME}")
        return
    if jsondata is None:
        raise print(f"File {HW_CONF_FILENAME} does not exist or contains invalid json")
    
    # {"display": {"type":"ssd1306", "config": {"sda_pin": 21, "scl_pin":22}}}
    display_conf = jsondata.get("display", None)
    if display_conf is not None:
        display_type = display_conf.get("type")
        print(f"Found display conf for {display_type}")
        if display_type == "ssd1306":
            from display_oled1306 import I2C1306
            print(f"Setting up display with config {display_conf}")
            hw.display = I2C1306(**display_conf.get("config"))
    
    

hw = Hardware()