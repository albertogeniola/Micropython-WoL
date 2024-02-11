import socket

import ubinascii

SOF_BROADCAST = 0x20


def create_magic_packet(macaddress: str) -> bytes:
    if len(macaddress) == 17:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, "")
    elif len(macaddress) != 12:
        raise ValueError("Incorrect MAC address format")

    return ubinascii.unhexlify("F" * 12 + macaddress * 16)


def send_magic_packet(
    *macs: str, ip_address: str, port: int, interface: str = None
) -> None:
    packets = [create_magic_packet(mac) for mac in macs]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if interface is not None:
        sock.bind((interface, 0))
    sock.setsockopt(socket.SOL_SOCKET, SOF_BROADCAST, 1)
    sock.connect((ip_address, port))
    for packet in packets:
        sock.send(packet)
    sock.close()
