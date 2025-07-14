import os
import time
from typing import Dict, List

import pandas as pd
from pynput import keyboard
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from zenml import step

# Stores Spotify credentials
TOKEN_CACHE = "data/.spotify_token.json"


@step
def collect_and_track(duration: int = 60, poll_interval: int = 1) -> pd.DataFrame:
    """
    Track typing speed and currently playing Spotify tracks + their genres.

    Args:
        duration (int): Total test duration (seconds).
        poll_interval (int): How often to poll Spotify (seconds).

    Returns:
        DataFrame: The combined results (tracks/wpm).
    """

    # Start capturing keystrokes
    key_times: List[float] = []
    listener = keyboard.Listener(on_press=lambda _: key_times.append(time.time()))
    listener.start()

    # Set up Spotify client (ensure you ran the OAuth flow already)
    auth = SpotifyOAuth(
        scope="user-read-playback-state",
        cache_path=TOKEN_CACHE
    )
    sp = Spotify(auth_manager=auth)

    # Poll loop: record when each track starts/stops
    start_time = time.time()
    last = {"id": None, "name": None, "artist": None, "start": start_time}
    segments: List[Dict] = []

    while time.time() - start_time < duration:
        now = time.time()
        playback = sp.current_user_playing_track()  # gets current track
        if playback and (item := playback.get("item")):
            tid = item["id"]
            name = item["name"]
            artist = item["artists"][0]["name"]
            aid = item["artists"][0]["id"]

            # Only add new segment if the track ID changed
            if tid != last["id"]:
                # close previous
                if last["id"] is not None:
                    segments.append({
                        "track_id": last["id"],
                        "track_name": last["name"],
                        "artist_id": last["artist_id"],
                        "artist_name": last["artist"],
                        "start": last["start"],
                        "end": now,
                    })
                # start new
                last = {
                    "id": tid,
                    "name": name,
                    "artist": artist,
                    "artist_id": aid,
                    "start": now,
                }

        time.sleep(poll_interval)

    # Stop listener and close final segment
    end_time = time.time()
    listener.stop()
    if last["id"] is not None:
        segments.append({
            "track_id": last["id"],
            "track_name": last["name"],
            "artist_id": last["artist_id"],
            "artist_name": last["artist"],
            "start": last["start"],
            "end": end_time,
        })

    # Fetch genres for all artists we saw.
    # Prior to Nov 2024, Spotify allowed users to extract song tempo through its
    # API, but this has been removed since.
    # https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api
    # As an alternative, we rely on extracting the genre based on the artist's
    # ID as an approximation to tempo.
    unique_artists = list({seg["artist_id"] for seg in segments})
    if unique_artists:
        details = sp.artists(unique_artists)
        artist_genre_map = {
            art["id"]: art.get("genres", [])
            for art in details["artists"]
        }
    else:
        artist_genre_map = {}

    # Build DataFrame rows with WPM + genres
    rows = []
    for seg in segments:
        presses = [t for t in key_times if seg["start"] <= t <= seg["end"]]
        duration_sec = seg["end"] - seg["start"]
        words = len(presses) / 5
        wpm = (words / duration_sec) * 60 if duration_sec > 0 else 0.0
        genres = artist_genre_map.get(seg["artist_id"], [])
        rows.append({
            "track_id": seg["track_id"],
            "track_name": seg["track_name"],
            "artist_name": seg["artist_name"],
            "genres": ", ".join(genres),
            "duration_seconds": duration_sec,
            "keypresses": len(presses),
            "wpm": wpm,
        })

    df = pd.DataFrame(rows)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/results.csv')
    print("Saved results to 'data/results.csv'")
    return df
