from dotenv import load_dotenv
import os

import requests


load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

def get_access_token(client_id, client_secret):
    '''
    Get access token for Spotify API
    
    Args:
    client_id (str): Spotify client ID
    client_secret (str): Spotify client secret
    
    Returns:
    access_token (str): Access token for Spotify API
    '''
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    auth_response_data = auth_response.json()  # Convert response to dictionary
    access_token = auth_response_data['access_token'] 

    return access_token


tracks = []
def get_playlist_tracks(playlist_id, access_token):
    '''
    Get tracks from a Spotify playlist
    
    Args:
    playlist_id (str): Spotify playlist ID
    access_token (str): Access token for Spotify API
    
    Returns:
    tracks (list): List of tracks in the playlist
    '''
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    
    while url:
        response = requests.get(url, headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        })
        
        json_response = response.json()  # Convert response to dictionary
        # print(json_response)
        tracks.extend(json_response['tracks']['items'])  # Add tracks from current page to list
        url = json_response.get('next')  # Get next page URL 
    
    return tracks


def spotify_main():
    my_playlist_id = '07icheaqv3vqfxPVzHQnwv?si=7233260e6a034fb9'

    access_token = get_access_token(client_id, client_secret)
    tracks = get_playlist_tracks(my_playlist_id, access_token)

    track_list = []
    for track in tracks:
        track_name = track['track']['name']
        artist_names = [artist['name'] for artist in track['track']['artists']]
        track_list.append((track_name, artist_names))
        # print(f"Track Name: {track_name}, Artist(s): {', '.join(artist_names)}")
    return track_list


if __name__ == '__main__':
    spotify_main()
