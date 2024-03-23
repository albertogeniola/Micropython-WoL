import socket

import ubinascii

SOF_BROADCAST = 0x20


def calculate_broadcast(ip, netmask) -> str:
    # Take the netmask, invert it and put it in OR with IP
    net_octects = netmask.split(".")
    ip_octects = ip.split(".")
    if len(net_octects) != 4 or len(ip_octects) != 4:
        raise ValueError("Invalid ip/mask specified")
    new_mask = []
    for i in range(4):
        octet = 255-int(net_octects[i])
        new_mask.append(octet | int(ip_octects[i]))
    return ".".join([str(x) for x in new_mask])


def _create_magic_packet(macaddress: str) -> bytes:
    if len(macaddress) == 17:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, "")
    elif len(macaddress) != 12:
        raise ValueError("Incorrect MAC address format")

    return ubinascii.unhexlify("F" * 12 + macaddress * 16)


def send_magic_packet(
    *macs: str, ip_address: str, port: int, interface: str = None
) -> None:
    packets = [_create_magic_packet(mac) for mac in macs]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if interface is not None:
        sock.bind((interface, 0))
    sock.setsockopt(socket.SOL_SOCKET, SOF_BROADCAST, 1)
    sock.connect((ip_address, port))
    for packet in packets:
        sock.send(packet)
    sock.close()
