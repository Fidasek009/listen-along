"""TOTP generation for Spotify authentication."""

import base64
import pyotp
from requests import get

from config import SECRET_CIPHER_URL
from logger import log

SECRET_CIPHER_DICT: dict[str, list[int]] = {}


def fetch_totp_secrets() -> None:
    """Fetch TOTP secrets from remote URL. Raises on failure."""
    global SECRET_CIPHER_DICT
    response = get(SECRET_CIPHER_URL, timeout=10)
    response.raise_for_status()
    SECRET_CIPHER_DICT = response.json()
    log.info(f"🔐: Loaded TOTP secrets, versions: {list(SECRET_CIPHER_DICT.keys())}")


def generate_totp(server_time: int) -> tuple[str, int]:
    """
    Generate TOTP for Spotify authentication.

    Args:
        server_time: Unix timestamp from Spotify server.

    Returns:
        Tuple of (totp_code, totp_version).
    """
    ver = max(map(int, SECRET_CIPHER_DICT))
    secret_cipher_bytes = SECRET_CIPHER_DICT[str(ver)]
    transformed = [e ^ ((t % 33) + 9) for t, e in enumerate(secret_cipher_bytes)]
    joined = "".join(str(num) for num in transformed)
    hex_str = joined.encode().hex()
    secret = base64.b32encode(bytes.fromhex(hex_str)).decode().rstrip("=")
    totp = pyotp.TOTP(secret, digits=6, interval=30)
    return totp.at(server_time), ver
