from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import time

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'Spotify-Session'


CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = "playlist-modify-public user-library-read"

# Spotify OAuth object
def get_auth_manager():
    return SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)

def get_spotify_client():
    token_info = session.get("token_info", None)
    if not token_info:
        return None

    # Refresh token if expired
    now = int(time.time())
    if token_info['expires_at'] - now < 60:
        auth_manager = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        )
        token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return spotipy.Spotify(auth=token_info['access_token'])

@app.route("/")
def home():
    # Check if user is logged in
    if not session.get("token_info"):
        return render_template("login.html")
    return render_template("index.html")

@app.route("/login")
def login():
    auth_manager = get_auth_manager()
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    auth_manager = get_auth_manager()
    code = request.args.get("code")
    token_info = auth_manager.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("home"))

@app.route("/create-playlist", methods=["POST"])
def create_playlist():
    token_info = session.get("token_info")
    if not token_info:
        return redirect(url_for("login"))

    sp = get_spotify_client()
    if sp is None:
        return redirect(url_for("login"))

    playlist_name = request.form.get("playlist_name")
    genre = request.form.get("genre")
    language = request.form.get("language")

    # Fetch tracks
    query = f"{genre} {language}"
    results = sp.search(q=query, type="track", limit=10)
    tracks = results["tracks"]["items"]

    if not tracks:
        return "No tracks found!"

    uris = [track["uri"] for track in tracks]

    # Create playlist
    user_id = sp.me()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, description=f"{genre} {language} mix")
    sp.playlist_add_items(playlist["id"], uris)

    # Prepare track details
    track_details = []
    for track in tracks:
        track_info = {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "image": track["album"]["images"][0]["url"],  # album cover
            "spotify_url": track["external_urls"]["spotify"]
        }
        track_details.append(track_info)

    return render_template("result.html", playlist_url=playlist["external_urls"]["spotify"], tracks=track_details)

if __name__ == "__main__":
    app.run(debug=True)
