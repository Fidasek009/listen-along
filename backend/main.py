"""Listen Along API - Spotify friend activity sync."""

import multiprocessing as mp

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from requests import get
from spotipy import Spotify

from config import COOKIE, ACTIVITY_URL, USER_AGENT
from logger import log, LOG_FILE
from auth import AccessToken
from player import player_run
from utils import uri_to_url, tail
from totp import fetch_totp_secrets

# Initialize TOTP secrets on startup
fetch_totp_secrets()

app = FastAPI()
api = Spotify()

if not COOKIE:
    log.error("❌: SP_DC_COOKIE environment variable is not set")
    raise RuntimeError("SP_DC_COOKIE environment variable is required")

token = AccessToken(COOKIE, api)
player: mp.Process | None = None


async def stop_player() -> None:
    """Stop the player process if running."""
    global player

    if player is None or not player.is_alive():
        return

    try:
        player.kill()
        player.join(timeout=2)
    except Exception as e:
        log.error(f"⛔: Error stopping player: {e}")
    finally:
        player = None
        log.info("⏹️: Stopped listening.")


@app.get("/", response_class=JSONResponse)
def read_root():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/log", response_class=PlainTextResponse)
async def get_log():
    """Get last 30 lines of the log file."""
    return tail(LOG_FILE, 30)


@app.get("/get-activity", response_class=JSONResponse)
async def get_activity():
    """Get friend activity from Spotify."""
    try:
        response = get(
            ACTIVITY_URL,
            headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log.error(f"❌: Failed to fetch activity: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch Spotify activity")


@app.get("/listen-along", response_class=JSONResponse)
async def listen_along(user_uri: str):
    """Start listening along to a friend."""
    global player

    await stop_player()

    player = mp.Process(target=player_run, args=(user_uri, token, api))
    player.start()
    log.info(f"▶️: Listening along to: {uri_to_url(user_uri)}")

    return {"status": "ok"}


@app.get("/stop-listening", response_class=JSONResponse)
async def stop_listening():
    """Stop listening along."""
    await stop_player()
    return {"status": "ok"}
