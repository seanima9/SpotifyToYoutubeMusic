from dotenv import load_dotenv
import os
import requests


# Load environment variables
load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

with open('/home/seanimani/personal_projs/playlist_conv/playlist_ids.txt', 'r') as file:
    playlist_ids = file.readlines()

spotify_playlist_id = playlist_ids[0].strip()

def get_access_token(client_id, client_secret):
    '''
    Obtain an access token for authenticating requests to the Spotify API.
    '''
    auth_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    if response.status_code == 200:  # If request was successful
        auth_response_data = response.json()
        return auth_response_data.get('access_token')
    else:
        raise Exception("Failed to retrieve access token from Spotify API.")


def get_playlist_tracks(playlist_id, access_token):
    '''
    Get the tracks from a Spotify playlist and return a list of dictionaries containing the track information.
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


def spotify_track_lister():
    '''
    Get the tracks from a Spotify playlist and return a list of tuples containing the track name and a list of artists.
    '''
    my_playlist_id = spotify_playlist_id
    
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
    spotify_track_lister()
