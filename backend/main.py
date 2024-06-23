from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from requests import get
from time import time, sleep
from os import getenv, SEEK_END
from spotipy import Spotify
from spotipy.exceptions import SpotifyException
import multiprocessing as mp
import logging as log

log.basicConfig(level=log.INFO,
                format="%(asctime)s\t%(levelname)s\t%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                filename="backend.log")

COOKIE = getenv("SP_DC_COOKIE")
WEB_TOKEN_URL = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
ACTIVITY_URL = "https://guc-spclient.spotify.com/presence-view/v1/buddylist"
SILENCE_URI = "spotify:track:57g9uWuZI1t822eLvEVQjn"
LISTENING_TIMEOUT = 15  # ammount of seconds to wait for new song before assuming user went offline

# ========== CLASSES ==========

class AccessToken:
    def __init__(self, sp_dc_cookie: str, api: Spotify):
        self.sp_dc_cookie = sp_dc_cookie
        self.accessToken = None
        self.client_id = None
        self.expiration = None
        self.api = api
        self.refresh()

    def __str__(self):
        return self.get()

    def get(self):
        if not self.isValid():
            self.refresh()

        return self.accessToken

    def isValid(self):
        return self.expiration > time() * 1000

    def refresh(self):
        res = get(WEB_TOKEN_URL, headers={"Cookie": f"sp_dc={self.sp_dc_cookie}"})
        res = res.json()
        self.accessToken = res["accessToken"]
        self.client_id = res["clientId"]
        self.expiration = res["accessTokenExpirationTimestampMs"]
        self.api.set_auth(self.accessToken)
        log.info("🔑: Token refreshed.")

# ========== AUX ==========

app = FastAPI()
api = Spotify()
token = AccessToken(COOKIE, api)
player = None

def player_run(user_uri: str):
    last_activity_ts = None
    song_duration = -1
    exit_counter = 0

    while True:
        activity = get(ACTIVITY_URL, headers={"Authorization": f"Bearer {token}"})
        users = activity.json()["friends"]

        for item in users:
            if item["user"]["uri"] == user_uri:
                track_uri = item["track"]["uri"]
                timestamp = item["timestamp"]
                offset = int(time() * 1000 - timestamp)

                # song changed
                if timestamp != last_activity_ts:
                    song_duration = play_song(track_uri, offset)
                    # failed to play song
                    if song_duration == -1:
                        exit()

                    last_activity_ts = timestamp
                    exit_counter = 0
                    break

                # song stopped
                if offset > song_duration:
                    if exit_counter == LISTENING_TIMEOUT:
                        log.info(f"⚠️: Song over. Duration: {song_duration // 1000}s, Offset: {offset // 1000}s")
                        exit()
                    else:
                        exit_counter += 1

                break

        sleep(1)


def play_song(song_uri: str, offset: int) -> int:
    features = api.audio_features(song_uri)
    duration = features[0]["duration_ms"]

    # silence is there in order for the player to stay active between songs
    songs = [SILENCE_URI]

    # the wanted song could've just ended
    if offset < duration:
        log.info(f"🎵: Playing song: {uri_to_url(song_uri)}")
        songs.insert(0, song_uri)

    try:
        api.start_playback(uris=songs, position_ms=offset)
    except SpotifyException as e:
        log.error(f"❌: Failed to play song with reason: {e.reason}")
        return -1

    return duration


def uri_to_url(uri: str) -> str:
    tokens = uri.split(':')
    return f"https://open.spotify.com/{tokens[1]}/{tokens[2]}"


def tail(fname: str, n: int) -> str:
    with open(fname, 'rb') as f:
        f.seek(0, SEEK_END)
        pos = f.tell()
        linecnt = 0

        while pos > 0:
            pos -= 1
            f.seek(pos)
            char = f.read(1)

            if char == b'\n':
                linecnt += 1
                if linecnt == n:
                    break
        
        # there are less than n lines in the file
        if pos == 0:
            f.seek(0)

        return f.read().decode('utf-8', 'replace')

# ========== API ==========

@app.get("/", response_class=JSONResponse)
def read_root():
    return {"Hello": "World"}


@app.get("/log", response_class=PlainTextResponse)
async def get_log():
    return tail("backend.log", 50)


@app.get("/get-activity")
async def get_activity():
    response = get(ACTIVITY_URL, headers={"Authorization": f"Bearer {token}"})

    try:
        return response.json()
    except:
        log.error(f"❌: {response.text}")
        return HTTPException(status_code=418, detail=response.text)


@app.get("/listen-along", response_class=JSONResponse)
async def listen_along(user_uri: str):
    global player

    if player:
        player.terminate()
        player.join()
        player = None

    player = mp.Process(target=player_run, args=(user_uri,))
    player.start()

    log.info(f"▶️: Listening along to: {uri_to_url(user_uri)}")
    return {"status": "ok"}


@app.get("/stop-listening", response_class=JSONResponse)
async def stop_listening():
    global player

    if player:
        player.terminate()
        player.join()
        player = None

    log.info("⏹️: Stopped listening.")
    return {"status": "ok"}
