import requests
import sys
import os
from dotenv import load_dotenv

script_dir = os.path.dirname(__file__)
sys.path.append(f'{script_dir}/..')

from utils.playlist_utils import update_playlist_ids
from auth.spotify_auth import get_access_token

load_dotenv(script_dir + "/../.env")
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')


def get_playlist_tracks(playlist_id, access_token):
    '''
    Get the tracks from a Spotify playlist and return a list of dictionaries containing the track information.

    Args:
    playlist_id (str): The ID of the Spotify playlist.
    access_token (str): The access token for authenticating requests to the Spotify API.

    Returns:
    list: The list of dictionaries containing the track information.
    '''
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    tracks = []
    while url:
        response = requests.get(url, headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        })
        
        if response.status_code == 200:  # If request was successful
            json_response = response.json()
            tracks.extend(json_response['items'])  # Append the tracks from the current page
            url = json_response.get('next')  # Update `url` for next page, if available
        else:
            raise Exception("Failed to retrieve playlist tracks from Spotify API.")
    
    return tracks


def spotify_track_lister(my_playlist_id):
    '''
    Get the tracks from a Spotify playlist and return a list of tuples containing the track name and a list of artists.

    Returns:
    list: The list of tuples containing the track name and a list of artists.
    '''
    
    access_token = get_access_token(client_id, client_secret)
    tracks = get_playlist_tracks(my_playlist_id, access_token)

    track_list = []
    for item in tracks:
        track = item['track']
        track_name = track['name']
        artist_names = track['artists'][0]['name']
        track_list.append((track_name, artist_names))
    return track_list


if __name__ == '__main__':
    spotify_playlist_id, youtube_playlist_id = update_playlist_ids()
    spotify_track_lister(spotify_playlist_id)
