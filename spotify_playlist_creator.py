import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
load_dotenv()


# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Define your Spotify developer credentials
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Scope for creating and modifying playlists
scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_path=".cache"
))

def create_playlist(name, description):
    try:
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, name, description=description)
        return playlist['id']
    except Exception as e:
        logging.error(f"Error creating playlist: {e}")
        return None

def add_songs_to_playlist(playlist_id, track_uris):
    try:
        sp.playlist_add_items(playlist_id, track_uris)
    except Exception as e:
        logging.error(f"Error adding songs to playlist: {e}")

def get_kannada_tracks(limit=10):
    try:
        # Search for top Kannada tracks using keywords
        results = sp.search(q="Kannada", type="track", limit=limit)
        return [track['uri'] for track in results['tracks']['items']]
    except Exception as e:
        logging.error(f"Error fetching Kannada tracks: {e}")
        return []

def main():
    print("Welcome to Spotify Playlist Creator!")
    print("1. Top Tracks by Genre")
    print("2. Top Kannada Tracks")
    
    choice = input("Enter the number of your choice: ")
    
    track_uris = []

    if choice == '1':
        genre = input("Enter a genre (e.g., rock, pop): ").strip().lower()
        track_uris = get_top_tracks_by_genre(genre, limit=10)
        
        if not track_uris:
            print("No tracks found for the specified genre.")
            return
        
        playlist_name = f"Top {genre.capitalize()} Tracks"
        playlist_description = "Generated playlist for top tracks by genre."
        
    elif choice == '2':
        track_uris = get_kannada_tracks(limit=10)
        
        if not track_uris:
            print("No Kannada tracks found.")
            return
        
        playlist_name = "Top Kannada Tracks"
        playlist_description = "Generated playlist featuring top Kannada songs."
    else:
        print("Invalid choice.")
        return

    playlist_id = create_playlist(playlist_name, playlist_description)
    if playlist_id:
        add_songs_to_playlist(playlist_id, track_uris)
        print(f"Playlist '{playlist_name}' created successfully!")
    else:
        print("Failed to create playlist.")

# Entry point
if __name__ == "__main__":
    main()
