"""Application configuration and constants."""

from os import getenv

COOKIE = getenv("SP_DC_COOKIE")
ACTIVITY_URL = "https://guc-spclient.spotify.com/presence-view/v1/buddylist"
TOKEN_URL = "https://open.spotify.com/api/token"
SERVER_TIME_URL = "https://open.spotify.com/"
SECRET_CIPHER_URL = "https://raw.githubusercontent.com/xyloflake/spot-secrets-go/refs/heads/main/secrets/secretDict.json"

LISTENING_TIMEOUT = 30
TOKEN_MAX_RETRIES = 3
TOKEN_RETRY_TIMEOUT = 0.5

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)
