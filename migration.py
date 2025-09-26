"""
YouTube Music to Spotify Playlist Migrator

This Flask application allows users to migrate playlists from YouTube Music to Spotify.
It handles OAuth authentication for both services and provides a web interface
for playlist selection and migration.

UCnvqgcY-BRFOP3wDPq9mpcw
"""

import os
import requests
from flask import Flask, request, redirect, session, url_for, render_template
from ytmusicapi import YTMusic
from dotenv import load_dotenv
import json


# Load environment variables
load_dotenv()

# Spotify API configuration
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SCOPES = (
    "user-read-private user-read-email playlist-read-private "
    "playlist-modify-private playlist-modify-public"
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Environment variables
BEARER_TOKEN = os.getenv("spotify_auth_token")
SPOTIFY_API_URL = os.getenv("spotify_api_endpoint")
SPOTIFY_CLIENT_ID = os.getenv("spotify_client_id")
SPOTIFY_REDIRECT_URI = os.getenv("spotify_redirect_url")
SPOTIFY_CLIENT_SECRET = os.getenv("spotify_client_secret")
YT_CLIENT_ID = os.getenv("yt_client_id")
YT_CLIENT_SECRET = os.getenv("yt_client_secret")

# Initialize YouTube Music API
ytmusic = YTMusic()

# Global variables
song_list = []
SPOTIFY_HEADERS = {
    'BASIC_AUTH': {"Authorization": f"Bearer {BEARER_TOKEN}"},
    'AUTH_CONTENT_TYPE': {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
}


@app.route("/")
def home():
    """Home page with YouTube Music user ID input form."""
    return '''
        <h1>YouTube Music → Spotify Migrator</h1>
        <p>Enter your YouTube Music user ID to begin migration:</p>
        <form action="/save_user" method="post">
            <label for="user_id">YouTube Music User ID:</label><br>
            <input type="text" id="user_id" name="user_id" required><br><br>
            <button type="submit">Continue</button>
        </form>
    '''

@app.route("/save_user", methods=["POST"])
def save_user():
    """Save YouTube Music user ID to session."""
    user_id = request.form.get("user_id")
    if not user_id:
        return "Please enter a valid user ID. <a href='/'>Go back</a>"
    
    session["user_id"] = user_id
    return f'User ID "{user_id}" saved! <a href="/pull_youtube_playlist">Begin Migration</a>'

@app.route("/pull_youtube_playlist", methods=["GET", "POST"])
def pull_youtube_playlist():
    """Fetch and display user's YouTube Music playlists."""
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    try:
        channel_id = session['user_id']
        user_params = ytmusic.get_user(channel_id)['playlists']['params']
        playlists = ytmusic.get_user_playlists(channelId=channel_id, params=user_params)

        if request.method == "POST":
            selected = request.form.get("playlist")
            if selected:
                playlist_info = json.loads(selected)
                session['yt_playlist_info'] = playlist_info
                return redirect(url_for("store_playlist"))

        return render_template("playlists.html", playlists=playlists)
    except Exception as e:
        return f"Error fetching playlists: {str(e)} <a href='/'>Go back</a>"

@app.route("/store_playlist")
def store_playlist():
    """Extract tracks from selected YouTube Music playlist."""
    if 'yt_playlist_info' not in session:
        return redirect(url_for('pull_youtube_playlist'))
    
    try:
        playlist_id = session.get('yt_playlist_info')['id']
        playlist_title = session.get('yt_playlist_info')['title']
        playlist = ytmusic.get_playlist(playlist_id)['tracks']
        song_list.clear()

        for song in playlist:
            if song.get('title') and song.get('artists'):
                track_info = {
                    'title': song['title'],
                    'artist': song['artists'][0]['name']
                }
                song_list.append(track_info)

        return redirect(url_for('spotify'))
    except Exception as e:
        return f"Error extracting playlist: {str(e)} <a href='/pull_youtube_playlist'>Go back</a>"


    except Exception as e:
        print(e)




@app.route("/spotify")
def spotify():
    """Redirect to Spotify login."""
    return '<h2>Ready to migrate!</h2><p>Click below to authenticate with Spotify:</p><a href="/login">Log in with Spotify</a>'

@app.route("/login")
def login():
    """Redirect user to Spotify authorization URL."""
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?client_id={SPOTIFY_CLIENT_ID}"
        f"&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope={SPOTIFY_SCOPES}"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """Handle Spotify OAuth callback and exchange code for access token."""
    code = request.args.get("code")
    error = request.args.get("error")
    
    if error:
        return f"Authorization failed: {error} <a href='/login'>Try again</a>"
    
    if not code:
        return "No authorization code received <a href='/login'>Try again</a>"

    try:
        token_response = requests.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": SPOTIFY_REDIRECT_URI,
                "client_id": SPOTIFY_CLIENT_ID,
                "client_secret": SPOTIFY_CLIENT_SECRET,
            },
            timeout=10
        )
        
        if token_response.status_code != 200:
            return f"Token exchange failed: {token_response.text} <a href='/login'>Try again</a>"

        token_data = token_response.json()
        session["access_token"] = token_data.get("access_token")
        session["refresh_token"] = token_data.get("refresh_token")
        session["token_type"] = token_data.get("token_type")

        # Update headers with new access token
        SPOTIFY_HEADERS['BASIC_AUTH'] = {
            "Authorization": f"Bearer {session['access_token']}"
        }
        SPOTIFY_HEADERS['AUTH_CONTENT_TYPE'] = {
            "Authorization": f"Bearer {session['access_token']}",
            "Content-Type": "application/json"
        }

        return redirect(url_for("profile"))
    except Exception as e:
        return f"Error during token exchange: {str(e)} <a href='/login'>Try again</a>"

@app.route("/profile")
def profile():
    """Fetch Spotify user profile and redirect to track search."""
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))
    
    try:
        profile_response = requests.get(
            "https://api.spotify.com/v1/me",
            headers=SPOTIFY_HEADERS['BASIC_AUTH'],
            timeout=10
        )

        if profile_response.status_code != 200:
            return (
                f"Failed to fetch profile: {profile_response.status_code}, "
                f"{profile_response.text} <a href='/login'>Try again</a>"
            )

        profile_data = profile_response.json()
        session['spotify_user_id'] = profile_data['id']
        
        return redirect(url_for("search_tracks"))
    except Exception as e:
        return f"Error fetching profile: {str(e)} <a href='/login'>Try again</a>"


@app.route("/search_tracks", methods=["POST", "GET"])
def search_tracks():
    """Create Spotify playlist and migrate tracks from YouTube Music."""

    access_token = session.get("access_token")

    if not access_token:
        return redirect(url_for("login"))
    
    if not song_list:
        return "No songs to migrate. <a href='/pull_youtube_playlist'>Go back</a>"
    
    try:
        # Create new Spotify playlist
        spotify_user_id = session['spotify_user_id']
        playlist_endpoint = f"{SPOTIFY_API_URL}/users/{spotify_user_id}/playlists"

        try:
            playlist_name = session.get('yt_playlist_info')['title']
        except Exception as e:
            print(f"failed {e}")

        payload = {
            "name": playlist_name,
            "description": "Playlist migrated from YouTube Music",
            "public": False
        }

        response = requests.post(
            playlist_endpoint,
            headers=SPOTIFY_HEADERS['AUTH_CONTENT_TYPE'],
            json=payload,
            timeout=10
        )
        
        if response.status_code != 201:
            return (
                f"Failed to create playlist: {response.status_code}, "
                f"{response.text} <a href='/login'>Try again</a>"
            )

        playlist_id = response.json()['id']
        session['playlist_id'] = playlist_id

        # Search for tracks and collect Spotify URIs
        spotify_song_ids = []
        songs_not_found = []

        for song in song_list:
            title = song.get("title")
            artist = song.get("artist")

            if not title or not artist:
                continue

            search_params = {
                "q": f"track:{title} artist:{artist}",
                "type": "track",
                "limit": 1,
            }

            search_response = requests.get(
                "https://api.spotify.com/v1/search",
                headers=SPOTIFY_HEADERS["BASIC_AUTH"],
                params=search_params,
                timeout=10
            )
            
            if search_response.status_code != 200:
                continue
                
            items = search_response.json().get("tracks", {}).get("items", [])

            if not items:
                songs_not_found.append(f"{title} - {artist}")
                continue
            
            spotify_song_id = items[0]["id"]
            spotify_song_ids.append(f"spotify:track:{spotify_song_id}")

        # Add tracks to playlist in batches of 100
        if spotify_song_ids:
            for i in range(0, len(spotify_song_ids), 100):
                batch = spotify_song_ids[i:i + 100]
                batch_payload = {"uris": batch}

                add_response = requests.post(
                    f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                    headers=SPOTIFY_HEADERS["AUTH_CONTENT_TYPE"],
                    json=batch_payload,
                    timeout=10
                )

                if add_response.status_code != 201:
                    return (
                        f"Error adding songs to playlist: {add_response.status_code}, "
                        f"{add_response.text}"
                    )

        # Prepare results message
        results = []
        if spotify_song_ids:
            results.append(f"Successfully migrated {len(spotify_song_ids)} songs!")
        if songs_not_found:
            results.append(f"Could not find {len(songs_not_found)} songs on Spotify:")
            results.extend([f"- {song}" for song in songs_not_found[:10]])  # Show first 10
            if len(songs_not_found) > 10:
                results.append(f"... and {len(songs_not_found) - 10} more")
        
        return "<br>".join(results) + '<br><br><a href="/">Start over</a>'
        
    except Exception as e:
        return f"Error during migration: {str(e)} <a href='/login'>Try again</a>"


if __name__ == "__main__":
    app.run(debug=True, port=8888, host='0.0.0.0')