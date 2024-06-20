from fastapi import FastAPI, HTTPException
import uvicorn
from requests import get
from time import time, sleep
from os import getenv
import spotipy as sp
import multiprocessing as mp

COOKIE = getenv("SP_DC_COOKIE")
WEB_TOKEN_URL = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
ACTIVITY_URL = "https://guc-spclient.spotify.com/presence-view/v1/buddylist"
LISTENING_TIMEOUT = 15  # ammount of seconds to wait for new song before assuming user went offline

# ========== AUX ==========

class AccessToken:
    def __init__(self, sp_dc_cookie: str):
        self.sp_dc_cookie = sp_dc_cookie
        self.accessToken = None
        self.client_id = None
        self.expiration = None
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


app = FastAPI()
token = AccessToken(COOKIE)
api = sp.Spotify(auth=token.get())
player = None

def player_run(user_uri: str):
    current_song = None
    exit_counter = 0

    while True:
        activity = get(ACTIVITY_URL, headers={"Authorization": f"Bearer {token}"})
        users = activity.json()["friends"]

        for item in users:
            if item["user"]["uri"] == user_uri:
                track_uri = item["track"]["uri"]
                offset = get_offset(track_uri, item["timestamp"])

                # song stopped
                if offset == -1:
                    if exit_counter == LISTENING_TIMEOUT:
                        print("⚠️: User is not listening to music anymore.")
                        exit()
                    else:
                        exit_counter += 1
                        break

                # song changed
                if track_uri != current_song:
                    play_song(track_uri, offset)
                    current_song = track_uri
                    exit_counter = 0

                break

        sleep(1)


def play_song(song_uri: str, offset: int):
    api.start_playback(uris=[song_uri], position_ms=offset)


def get_offset(song_uri: str, timestamp_ms: int) -> int:
    offset = int(time() * 1000 - timestamp_ms)
    result = api.audio_features(song_uri)
    duration = result[0]["duration_ms"]

    if offset > duration:
        offset = -1

    return offset


# ========== API ==========

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/get-activity", response_model=dict)
async def get_activity():
    response = get(ACTIVITY_URL, headers={"Authorization": f"Bearer {token}"})

    try:
        return response.json()
    except:
        print("⛔: Invalid token.")
        print(response)
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port="8000")
