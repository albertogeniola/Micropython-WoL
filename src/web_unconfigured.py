import machine

from configuration import _configuration
from device import _dev_registry
from microdot import Microdot, send_file
from web_common import make_json_response, BadRequest


app = Microdot()
scanned_networks = []

def _reboot(*args, **kwargs):
    print("Hard rebooting...")
    machine.reset()
    return


@app.errorhandler(Exception)
def runtime_error(request, exception):
    return make_json_response(data=None, error=f"Unhandled error occurred: {str(exception)}", status_code=500)


@app.route("/")
async def home(request):
    return send_file("static/install.html")


@app.route('/static/css/<path:path>')
async def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    target = 'static/css/' + path
    return send_file(target)


@app.route('/api/v1/scan')
async def scan_wifi(request):
    # Return scanned results
    return make_json_response(data=scanned_networks)


@app.route("/api/v1/install", methods=["POST"])
async def install(request):
    # Parse received configuration. It must contain:
    # Password for the admin account
    # Network configuration
    data = request.json
    if data is None:
        raise BadRequest("Missing or invalid json data received")

    network = data["network"]
    password = data["password"]

    # Validate password
    if password is None or len(password) < 6:
        raise BadRequest("The password is too short")

    # Validate network
    _configuration.admin_password = password
    _configuration.ssid = network["ssid"]
    _configuration.ssid_password = network["ssidPassword"]
    _configuration.static_ip = network["ip"]
    _configuration.netmask = network["netmask"]
    _configuration.gateway = network["gateway"]
    _configuration.dns = network["dns"]

    _configuration.save_to_file("install.json")

    # Save device list
    _dev_registry.persist()

    timer = machine.Timer(-1)
    timer.init(mode=machine.Timer.ONE_SHOT, period=5000, callback=_reboot)
    return make_json_response(data="Applying configuration...", status_code=200)
