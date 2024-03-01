# ESP32 WOL: a tiny Wake-on-Lan delegate

<img src="docs/images/case-3d/Front_PETG.jpg" height=300>
<img src="docs/images/case-3d/Interior.jpg" height=300>

## What is ESP32-WOL?
ESP32-WoL is a firmware, written for the Expressif ESP32 device in microptyhon,
that turns the ESP32 device into a web-service to send wake-on-lan packets on 
your local network.

This tool is suited for people who want to turn on their PC-devices via Wake-On-Lan,
but cannot do that using their current home gateways or have no domotic/server device
where to install such a service.

## Why ESP32?
The ESP32 is a small, cheap, low-power and powerful micro-controller.
This project turns that tiny chip into a Wake-On-Lan service provider 
exposed via a self-hosted web-ui, which can be reached from all-over the internet. 

Of course, you might use other devices/servers to do the same thing.
But, if you don't have any, and you just need a small, power-efficient device to 
turn on you other devices on the network, the ESP32-WoL is what you are looking for.

Let's have a look at some possible alternatives in the following table.

|                     | ESP32-WoL    | Raspberry with HA | Home Server |
|---------------------|--------------|:-----------------:|------------:|
| Hardware cost       | < 10 USD     |     ~ 60 USD      |    100+ USD |
| Power consumption   | < 1 W        |       4~5 W       |      ~ 15 W |
| Occupied space      | 2 coins size | Credit card size  |   Mini ITX+ |
| Installation effort | Minimum      |      Medium       |        High |

As you can see, the ESP32-WoL is way cheaper than the HomeAssistant solution, smaller and 
less power hungry. However, it is not as general purpose as HomeAssistant or as full featured
home server. Therefore, here's the advice: **rely on the ESP32-WoL when you don't have an 
always-on Raspberry running HA nor home-server or if you need to wake-up devices over multiple
VLANs/subnets**. 

In my specific case, I needed to run WoL packets into different subnets, and I had my HomeAssistant device into another subnet. 

## Installation instructions
In order to install ESP32-WoL firmware, you should apply the following procedure.

1. Flash micropython firmware to your ESP32 device
2. Install this program on the ESP32
3. Configure the ESP32-WoL
4. Configure your router to allow internet traffic to the ESP32-WoL
5. Add WoL devices

### 1. Flashing micropython firmware
This step is only required if you ESP32 device is not yet flashed with a micropython firmware.
[Here](https://micropython.org/download/esp32/) and [here](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html#deploying-the-firmware) 
you find the official instructions to do so.

For instance, to install the Micropython firmware on WROOM ESP32 device connected to port COM5, just download the latest image from the website above (at the time of writing is ESP32_GENERIC-20240105-v1.22.1.bin) and install as follows:

```bash 
python3 -m esptool esptool.py --port COM5 write_flash -z 0x1000 ESP32_GENERIC-20240105-v1.22.1.bin 
```

Please note down the specific version of the firmware (in this case, `1.22.1`). You will need it later on.

**Note: this tool has been tested only with v1.22.1 (2024-01-05) micropython firmware**. 
There is no guarantee it is compatible with other firmware versions. 

### 2. Install this software into the ESP32
Once the ESP32 device is capable of running python software, you need to upload the python scripts into the device to turn it into a fully functional ESP32-WOL. 

To do so, first download the repository source code.

```bash
git clone https://github.com/albertogeniola/ESP32-WoL.git
```

Then let's create a virtual-env and install the required package dependency to run our python upload script.

```bash
cd ESP32-WoL
python3 -m venv .venv
source .venv/bin/activate # or if you are on windows: .venv\Scripts\activate.bat
pip install -r requirements.txt
```

After that, we need to install the cross-compilation library (mpy-cross).
Retrieve the specific version of your micropython installed version (in this example was `1.22.1`) and install the corresponding mpy-cross package, as follows:

```bash
python -m pip install mpy-cross==1.22.1
```

Remember: if you using a different version of micropython, change the `1.22.1` parameter accordingly.

At this point, we can now perform the program upload. To do so, disconnect your ESP32 device and run the following command. 
Replace `_COM_PORT_NAME_OR_TTY_` with the serial port path/name of your ESP32 device. On Windows, they are usually `COMX` (where X is an integer); on Linux it is in the form of `/dev/ttyUSB0`

```bash
python upload_mpy.py _COM_PORT_NAME_OR_TTY_
```

Then, plug the ESP32 device via USB within 30 seconds: the flashing process will start. 

```
...
Pre-compiling ...
Pre-compiling ...
Pre-compiling ...
Uploading boot.py, main.py and hw.json
Waiting 30 seconds for pyboard ....
```

When you are done, the onboard device led should start blinking slowly: that means the device entered the "installation mode". If that's the case, you can proceed with the next section. If the led does not blink, it probably means some error occurred during the upload or flash process. You should start over and make sure to follow every step again.

### 3. Configure the ESP32-WoL
At this stage, the ESP32 is flashed with micropython and it has been loaded with the necessary python files to run our Web service. We can now run the configuration wizard.

The first step is to use your laptop or smartphone to connect to the Access Point named "ESP_WOL" that the ESP32 sets up when it is in installation mode. Connect to that WIFI using the the following password: `espwol123`.

Once connected to the WiFi, open a browser and navigate to `http://192.168.4.1`. 
From that page, you will configure:
- The admin's password to log in to the ESP32 tool
- Your local WiFi SSID where the ESP32 should connect to
- Advanced network setup (static ip address for the ESP32)

*Note: you probably want to assign the ESP32 a static IP address.
You can do that via this web-ui or by configuring a DHCP static lease 
(or MAC-binding) at router/gateway/cpe level.* 

Once the form is submitted, the ESP32-WoL will reboot itself and attempt to connect
to the provided WiFi network, using the SSID and Password you provided via the form.
During this process, the onboard led will blink quickly. 

If the configuration fails, the device will reboot and put itself into installation mode
again. You will recognize that as the onboard led will start blinking slowly as it did 
before. If that happens, you should connect again to ESP_WOL wifi and start over the 
configuration.

On the contrary, if the ESP32 correctly connects to the target WiFi,
the onboard led will turn to FIXED-ON. When this happens, the web-ui should automatically redirect you to the ESP32-WoL web-administration page. If that does not happen, you can reach it by typing `http://<target_ip>` where `target_ip` is the IP address that the ESP32 device has been assigned via DHCP or has bound statically.
The ESP32_WOL will advertise its IP via bluetooth le. You can use the `BLE Scanner` android app to get this info: you jus need to launch the APP and scan for BLE device. You'll see an entry named `ESP32-WoL <IP_ADDRESS>`.

### 4. Allow internet access to ESP32-WoL
In order to be functional to its original objective, the ESP32-WoL should be accessible
from internet. This means that you should:
- Make sure the ESP32 always gets the same IP on the LAN
- Enable port-forwarding from WAN IP to ESP32 internal IP, on TCP port 80 
- Optionally configure dynamic dns on your router device in case you have a dynamic external IP address from the ISP

Specific instructions on how to achieve such configuration objectives are out of the scope of this document, as every cpe/router device might differ. The internet is full of tutorials on how to do so, though. Just google for your router model and "how to port forward" o "how to static DHCP lease" and you should find some nice tutorial to help you out.

### 5. Add WoL devices
If you made up to this stage, congratulations: you are done. 
It is now time to register the LAN devices you would like to wake up via the ESP32-WoL, so that you don't need to remember their MAC address by memory.

To do so, simply access the Web-UI of the ESP32-WoL at `http://mywol` o `http://<IP_OF_ESP32_WOL>`, log in with the admin password and add a new device. For a new device to be valid you must specify its mac address and a name. You could optionally set also its IP (in case it is static): if you do so, the ESP32-WoL will be able to check whether the target device is already ON or OFF.

*Note: if you don't specify the IP address of the target device, its "ON" or "OFF" status will be unreliable, but WoL packets will be delivered in any case, when you send them.*


## Advanced Topics
### API interactions
It is possible to interact with ESP32-WOL via REST APIs. You can find the API Open Specs in the `docs/swagger.yaml` file within this repository.
You can also test it directly via the nice swagger UI [from here](https://albertogeniola.github.io/ESP32-WoL/swagger).


### 3D printable case
This repository contains a STL model for 3D printing. 
The model is designed for the `JZK ESP-WROOM-32 ESP-32` ([available here on Amazon](https://p-nt-www-amazon-it-kalias.amazon.it/gp/product/B071JR9WS9/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)).

The 3D printable model is designed to hold an oled display ssd1306 and has enough space for holding a small piezo-buzzer inside the case. 

<a href="docs/images/case-3d/Front_PLA.jpg"><img src="docs/images/case-3d/Front_PLA.jpg" height=300></a>
<a href="docs/images/case-3d/Composizione.png"><img src="docs/images/case-3d/Composizione.png" height=300></a>
<a href="docs/images/case-3d/colored.png"><img src="docs/images/case-3d/colored.png" height=300></a>

You can find the 3D printable files on [ThingVerse](https://www.thingiverse.com/thing:6511323).


### Hardware Setup
TODO

### Configure wifi via config.json
TODO

## Some Screenshots
<a href="docs/images/login.png"><img src="docs/images/login.png" width=300></a>
<a href="docs/images/main.png"><img src="docs/images/main.png" width=300></a>
