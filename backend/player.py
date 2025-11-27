"""Music player functionality for listen-along feature."""

from time import time, sleep

from requests import get
from spotipy import Spotify
from spotipy.exceptions import SpotifyException

from config import ACTIVITY_URL, USER_AGENT, LISTENING_TIMEOUT
from logger import log
from auth import AccessToken


def play_song(api: Spotify, song_uri: str, song_name: str, offset: int) -> int:
    """
    Start playing a song at the given offset.

    Args:
        api: Authenticated Spotify API client.
        song_uri: Spotify URI of the track.
        song_name: Display name of the track.
        offset: Playback position in milliseconds.

    Returns:
        Track duration in milliseconds, or -1 on failure.
    """
    features = api.audio_features(song_uri)
    duration = features[0]["duration_ms"]

    try:
        api.start_playback(uris=[song_uri], position_ms=offset)
    except SpotifyException as e:
        log.error(f"❌: Failed to play song: {e.reason}")
        return -1

    if offset >= duration:
        return 0

    offset_sec = offset // 1000
    minutes = offset_sec // 60
    seconds = offset_sec % 60
    log.info(f"🎵: Playing: {song_name} ({minutes}:{seconds:02d})")
    return duration


def player_run(user_uri: str, token: AccessToken, api: Spotify) -> None:
    """
    Main player loop that syncs playback with a friend's activity.

    Args:
        user_uri: Spotify URI of the friend to follow.
        token: AccessToken instance for API authentication.
        api: Authenticated Spotify API client.
    """
    last_activity_ts = None
    song_duration = -1
    exit_counter = 0

    while True:
        try:
            activity = get(
                ACTIVITY_URL,
                headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
            )
            users = activity.json().get("friends", [])
        except Exception as e:
            log.error(f"❌: Failed to fetch activity: {e}")
            sleep(5)
            continue

        for item in users:
            if item["user"]["uri"] != user_uri:
                continue

            timestamp = item["timestamp"]
            offset = int(time() * 1000 - timestamp)

            if timestamp != last_activity_ts:
                track_uri = item["track"]["uri"]
                track_name = item["track"]["name"]
                song_duration = play_song(api, track_uri, track_name, offset)
                if song_duration == -1:
                    return

                last_activity_ts = timestamp
                exit_counter = 0
                break

            if offset > song_duration:
                if exit_counter >= LISTENING_TIMEOUT:
                    log.info(f"⚠️: User stopped listening. (waited {(offset - song_duration) // 1000}s)")
                    return
                exit_counter += 1

            break

        sleep(1)
