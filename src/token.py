import json
import time

import ubinascii

from configuration import _configuration
from md5 import digest


def create_token(username: str, expire_seconds: int = 86400):  # defaults to 1d exp
    now = time.time()
    expiration = now + expire_seconds
    data = {
        "expiration": expiration,
        "issued_on": now,
        "username": username
    }
    message = json.dumps(data)
    clear_hmac = message + _configuration.secret
    signature = digest(clear_hmac.encode("utf8"))
    text = message+"##"+signature
    token = ubinascii.hexlify(text.encode("utf8"))
    return token


def verify_token(token) -> bool:
    # De-Hexify the token
    try:
        unhexed = ubinascii.unhexlify(token)
    except:
        print("Could not de-hexify the token")
        return False

    # Retrieve original message and signature
    clear_hmac = unhexed.decode("utf8")
    parts = clear_hmac.split("##")
    if len(parts) != 2:
        print("Invalid token: cannot get message and signature.")
        return False
    message, signature = parts

    # Verify the signature
    clear_hmac = message + _configuration.secret
    target_signature = digest(clear_hmac.encode("utf8"))
    if signature != target_signature:
        print(f"Invalid signature: provided '{signature}', expected '{target_signature}'")
        return False
    else:
        return True

