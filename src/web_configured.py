import gc

import magic_packet
import uping
from configuration import _configuration
from constants import BROADCAST_IP
from device import _dev_registry
from microdot_asyncio import Microdot, send_file
from token import verify_token, create_token
from web_common import make_json_response, BadRequest
import ubinascii
import network
from hardware_initializer import hw


app = Microdot()


class AuthenticationError(Exception):
    pass


def check_auth_token(request):
    token = request.headers.get("wol-token")
    if token is not None and verify_token(token):
        return
    raise AuthenticationError()


@app.errorhandler(Exception)
def runtime_error(request, exception):
    return make_json_response(data=None, error=f"Unhandled error occurred: {str(exception)}", status_code=500)


@app.errorhandler(AuthenticationError)
def runtime_error(request, exception):
    return make_json_response(data=None, error="Missing or invalid authentication token (wol-token) in headers", status_code=403)


@app.route("/")
async def home(request):
    return send_file("static/index.html")


@app.route('/static/<path:path>')
async def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path)


@app.route("/api/v1/system/alive", methods=["GET", "OPTIONS"])
async def check_alive(request):
    return make_json_response(data="System alive!", status_code=200,
                              additional_headers={
                                  "Access-Control-Allow-Origin": "*",
                                  "Access-Control-Allow-Methods": "GET, OPTIONS",
                                  "Access-Control-Allow-Headers": "*"
                              })


@app.route("/api/v1/users/login", methods=["POST"])
async def login(request):
    username = str(request.json["username"])
    password = str(request.json["password"])
    if username == "admin" and _configuration.admin_password == password:
        token = create_token(username)
        return make_json_response({"token": token})
    else:
        return make_json_response(data=None, error="Invalid login", status_code=403)


@app.route("/api/v1/devices", methods=["GET"])
async def get_devices(request):
    check_auth_token(request)
    devs = _dev_registry.get_devices()
    encoded = make_json_response(data=[devs[x].to_dict() for x in devs], error=None, status_code=200)
    return encoded


@app.route("/api/v1/devices", methods=["POST"])
async def add_device(request):
    check_auth_token(request)
    if "mac" not in request.json:
        raise BadRequest("Missing mac property")
    if "name" not in request.json:
        raise BadRequest("Missing name property")
    dev = _dev_registry.add_update_device(mac=request.json["mac"], name=request.json["name"], ip=request.json.get("ip"))
    encoded = make_json_response(dev.to_dict(), error=None, status_code=200)
    return encoded


@app.route("/api/v1/devices/<mac>", methods=["DELETE"])
async def add_device(request, mac):
    check_auth_token(request)
    dev = _dev_registry.get_devices().get(mac)
    if dev is None:
        return make_json_response(data=None, error="No device with that MAC is available", status_code=404)
    _dev_registry.delete_device(mac=mac)
    encoded = make_json_response("Device deleted", error=None, status_code=200)
    return encoded


@app.route("/api/v1/devices/<mac>/wol", methods=["POST"])
async def wol(request, mac):
    check_auth_token(request)
    # Note: we don't explicitly check for a stored device with that mac. We allow to wake up any MAC.
    dev = _dev_registry.get_devices().get(mac)
    dev_name =  dev.name if dev is not None else "Unknown"
    hw.display.notify_wol(mac, dev_name)
    magic_packet.send_magic_packet(mac, ip_address=BROADCAST_IP, port=9)
    encoded = make_json_response("Packet has been sent")
    return encoded


@app.route("/api/v1/devices/<ip>/ping", methods=["GET"])
def ping(request, ip):
    gc.collect()
    check_auth_token(request)
    transmitted, received = uping.ping(host=ip, count=1, timeout=1000, quiet=True)
    encoded = make_json_response(transmitted == received)
    return encoded


@app.route("/api/v1/system/info", methods=["GET"])
def system_info(request):
    check_auth_token(request)
    bytes_used_memory = gc.mem_alloc()
    bytes_free_memory = gc.mem_free()
    nic = network.WLAN(network.STA_IF)
    ip, netmask, gateway, dns = nic.ifconfig()
    ssid = nic.config('essid')
    signal_strength = nic.status('rssi')
    mac_address = nic.config('mac')
    mac_address = ubinascii.hexlify(mac_address, ':').decode().upper()

    data = {
        "memory": {
            "used": bytes_used_memory,
            "free": bytes_free_memory
        },
        "network": {
            "ssid": ssid,
            "mac": mac_address,
            "ip": ip,
            "netmask": netmask,
            "gateway": gateway,
            "dns": dns,
            "signalStrength": signal_strength
        },
        "caller": {
            "ip": request.client_addr[0]
        }
    }
    encoded = make_json_response(data)
    return encoded
