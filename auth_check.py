from utils.spotify_auth import get_spotify_client

sp = get_spotify_client()
print("Authenticated as:", sp.me()["display_name"])
