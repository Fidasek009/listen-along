"""Spotify authentication and token management."""

from time import time, time_ns, sleep
from email.utils import parsedate_to_datetime

from requests import Session, get
from requests.exceptions import HTTPError
from spotipy import Spotify

from config import (
    TOKEN_URL,
    SERVER_TIME_URL,
    USER_AGENT,
    TOKEN_MAX_RETRIES,
    TOKEN_RETRY_TIMEOUT,
)
from logger import log
from totp import generate_totp, fetch_totp_secrets


def fetch_server_time(session: Session) -> int:
    """Fetch Spotify server time from edge server using Date header."""
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    response = session.head(SERVER_TIME_URL, headers=headers, timeout=15)
    response.raise_for_status()
    date_hdr = response.headers.get("Date")
    if not date_hdr:
        raise Exception("Missing 'Date' header from server")
    return int(parsedate_to_datetime(date_hdr).timestamp())


class AccessToken:
    """Manages Spotify access token using sp_dc cookie authentication."""

    def __init__(self, sp_dc_cookie: str, api: Spotify):
        self.sp_dc_cookie = sp_dc_cookie
        self.access_token: str | None = None
        self.client_id: str | None = None
        self.expiration: int | None = None
        self.api = api
        self.session = Session()
        self.refresh()

    def __str__(self) -> str:
        return self.get() or ""

    def get(self) -> str | None:
        """Get valid access token, refreshing if needed."""
        if not self.is_valid():
            self.refresh()
        return self.access_token

    def is_valid(self) -> bool:
        """Check if current token is still valid."""
        return self.expiration is not None and self.expiration > time() * 1000

    def _build_token_params(self, server_time: int, reason: str = "transport") -> dict:
        """Build query parameters for token request."""
        otp_value, totp_ver = generate_totp(server_time)
        client_time = int(time_ns() / 1000 / 1000)

        return {
            "reason": reason,
            "productType": "web-player",
            "totp": otp_value,
            "totpServer": otp_value,
            "totpVer": totp_ver,
            "sTime": server_time,
            "cTime": client_time,
        }

    def _check_token_validity(self, access_token: str, client_id: str | None) -> bool:
        """Verify token works with Spotify API."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": USER_AGENT,
        }
        if client_id:
            headers["Client-Id"] = client_id
        try:
            response = get("https://api.spotify.com/v1/me", headers=headers, timeout=15)
            return response.status_code == 200
        except Exception:
            return False

    def _try_get_token(self, headers: dict, reason: str) -> bool:
        """Attempt to get and validate a token with given reason."""
        server_time = fetch_server_time(self.session)
        params = self._build_token_params(server_time, reason)
        res = self.session.get(TOKEN_URL, params=params, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()

        access_token = data.get("accessToken", "")
        client_id = data.get("clientId", "")

        if access_token and self._check_token_validity(access_token, client_id):
            self.access_token = access_token
            self.client_id = client_id
            self.expiration = data.get("accessTokenExpirationTimestampMs")
            self.api.set_auth(self.access_token)
            return True
        return False

    def refresh(self) -> None:
        """Refresh access token with retry logic."""
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Referer": "https://open.spotify.com/",
            "App-Platform": "WebPlayer",
            "Cookie": f"sp_dc={self.sp_dc_cookie}",
        }

        last_error = ""
        secrets_refreshed = False

        for attempt in range(TOKEN_MAX_RETRIES):
            try:
                if self._try_get_token(headers, "transport"):
                    log.info("🔑: Token refreshed successfully.")
                    return

                if self._try_get_token(headers, "init"):
                    log.info("🔑: Token refreshed successfully (init mode).")
                    return

                last_error = "Token validation failed"

            except HTTPError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                log.warning(f"Token refresh attempt {attempt + 1} failed: {last_error}")

                if "totpVerExpired" in e.response.text and not secrets_refreshed:
                    log.info("🔄: TOTP secrets expired, fetching updated secrets...")
                    try:
                        fetch_totp_secrets()
                        secrets_refreshed = True
                        continue
                    except Exception:
                        pass

            except Exception as e:
                last_error = str(e)
                log.warning(f"Token refresh attempt {attempt + 1} failed: {last_error}")

            if attempt < TOKEN_MAX_RETRIES - 1:
                sleep(TOKEN_RETRY_TIMEOUT)

        log.error(f"❌: Failed to refresh token after {TOKEN_MAX_RETRIES} attempts: {last_error}")
