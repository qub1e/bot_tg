import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from spotipy.exceptions import SpotifyException

# Spotify credentials
SPOTIFY_CLIENT_ID = "46a656ffd21343b89266d8d3aa4f1ad3"
SPOTIFY_CLIENT_SECRET = "ac3e21281aaf46dfa9ff191d679e0753"
REDIRECT_URI = "http://localhost:8080/callback"

# Authenticate with Spotify using OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read"
))

# Fetch tracks for a specific genre
def fetch_tracks_by_genre(genre, limit=50):
    results = sp.search(q=f"genre:{genre.lower()}", type="track", limit=limit)
    tracks = []
    for track in results['tracks']['items']:
        tracks.append({
            "name": track['name'],
            "artist": track['artists'][0]['name'],
            "album": track['album']['name'],
            "release_date": track['album']['release_date'],
            "popularity": track['popularity'],
            "id": track['id'],
            "genre": genre
        })
    return tracks

# Fetch audio features in batches
def fetch_audio_features_in_batches(track_ids, batch_size=50):
    audio_features = []
    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i + batch_size]
        try:
            features = sp.audio_features(batch)
            if features:
                audio_features.extend(features)
        except SpotifyException as e:
            print(f"Error fetching batch {batch}: {e}")
            continue
    return audio_features

# Fetch data for all genres
genres = [
    "Pop", "Rock", "Jazz", "Hip-Hop", "Classical", "EDM", "Country",
    "Reggae", "Blues", "Metal", "Folk", "Other"
]
all_tracks = []

for genre in genres:
    print(f"Fetching tracks for genre: {genre}")
    try:
        all_tracks.extend(fetch_tracks_by_genre(genre, limit=50))
    except Exception as e:
        print(f"Error fetching tracks for genre {genre}: {e}")

# Convert to DataFrame
tracks_df = pd.DataFrame(all_tracks)

# Save basic track data to CSV
tracks_df.to_csv("spotify_music_data_extended_genres.csv", index=False)

# Fetch and merge audio features
track_ids = tracks_df['id'].tolist()
audio_features = fetch_audio_features_in_batches(track_ids)
audio_features_df = pd.DataFrame(audio_features)

# Merge and save the full data
if not audio_features_df.empty:
    full_data = pd.concat([tracks_df, audio_features_df], axis=1)
    full_data.to_csv("spotify_music_data_with_audio_features.csv", index=False)
else:
    print("No audio features found. Check API permissions or data.")