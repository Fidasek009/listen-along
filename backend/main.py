from fastapi import FastAPI, HTTPException
from requests import get
from time import time, sleep
from os import getenv
from spotipy import Spotify
import multiprocessing as mp

COOKIE = getenv("SP_DC_COOKIE")
WEB_TOKEN_URL = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
ACTIVITY_URL = "https://guc-spclient.spotify.com/presence-view/v1/buddylist"
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
                    last_activity_ts = timestamp
                    exit_counter = 0
                    break

                # song stopped
                if offset > song_duration:
                    if exit_counter == LISTENING_TIMEOUT:
                        print(f"⚠️: Song over. Duration:{song_duration // 1000}s, Offset:{offset // 1000}s")
                        exit()
                    else:
                        exit_counter += 1

                break

        sleep(1)


def play_song(song_uri: str, offset: int) -> int:
    result = api.audio_features(song_uri)
    duration = result[0]["duration_ms"]

    if offset < duration:
        api.start_playback(uris=[song_uri], position_ms=offset)
    else:
        print(f"⚠️: Song over. Duration:{duration // 1000}s, Offset:{offset // 1000}s")

    return duration

# ========== API ==========

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/get-activity")
async def get_activity():
    response = get(ACTIVITY_URL, headers={"Authorization": f"Bearer {token}"})

    try:
        return response.json()
    except:
        print("⛔: Invalid token.")
        print(response.text)
        return HTTPException(status_code=418, detail="Invalid token.")


@app.get("/listen-along")
async def listen_along(user_uri: str):
    global player

    if player:
        player.terminate()
        player.join()
        player = None

    player = mp.Process(target=player_run, args=(user_uri,))
    player.start()
    return {"status": "ok"}


@app.get("/stop-listening")
async def stop_listening():
    global player

    if player:
        player.terminate()
        player.join()
        player = None

    return {"status": "ok"}
