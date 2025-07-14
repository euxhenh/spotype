import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

load_dotenv()


def get_spotify_client():
    return spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(),
        auth_manager=SpotifyOAuth(
            scope="user-read-recently-played",
            cache_path="data/.spotify_token.json",
            show_dialog=True  # forces re-auth if needed
        )
    )
