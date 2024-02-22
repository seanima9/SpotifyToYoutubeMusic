from dotenv import load_dotenv
import os
import requests
import re

# Load environment variables
load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

script_dir = os.path.dirname(__file__)
full_file_path = os.path.join(script_dir, 'playlist_ids.txt')


##################### Getting Playlist IDs #####################


def get_playlist_url(service_name):
    while True:
        url = input(f"Enter {service_name} playlist URL: ")
        playlist_id = extract_playlist_id(url)
        if playlist_id is not None:
            global songs_list_wipe
            songs_list_wipe = True
            print(f"Successfully extracted {playlist_id} for {service_name} \n")
            return playlist_id

        print(f"Invalid {service_name} playlist URL. Please try again. \n")

        
def extract_playlist_id(url):
    '''
    Extract the playlist ID from a Spotify or YouTube playlist URL.
    
    Args:
    url (str): The URL of the Spotify or YouTube playlist.
    
    Returns:
    str: The ID of the Spotify or YouTube playlist.
    '''
    yt_pattern = re.compile(r"music\.youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)")
    spot_pattern = re.compile(r"open\.spotify\.com/playlist/([a-zA-Z0-9]+)")

    yt_match = yt_pattern.search(url)
    if yt_match:
        return yt_match.group(1)
    
    spot_match = spot_pattern.search(url)
    if spot_match:
        return spot_match.group(1)
    
    # If the URL is not a Spotify or YouTube playlist URL
    return 


def update_playlist_ids():
    '''
    Check for id prescence in playlist_ids.txt and ask for new ids if not present.
    Also ask if they want to update it regardless.
    
    Returns:
    None
    '''
    global songs_list_wipe
    songs_list_wipe = False
    response = '0'
    try:
        with open(full_file_path, 'r') as f:
            lines = f.readlines()
            spotify_id = lines[0].strip()
            youtube_id = lines[1].strip()

    except (FileNotFoundError, IndexError):
        print("\nMissing IDs in playlist_ids.txt \n")
        spotify_id = get_playlist_url("Spotify")
        youtube_id = get_playlist_url("YouTube")
        response = '1'

    while True:
        response = input(str("\n1. Keep using the current Spotify and YouTube playlists\n"
                         "2. Update the Spotify and YouTube playlists\n"
                         "3. Update the Spotify playlist\n"
                         "4. Update the YouTube playlist\n: "))
        
        if response == '1':
            break
        elif response == '2':
            spotify_id = get_playlist_url("Spotify")
            youtube_id = get_playlist_url("YouTube")
            break
        elif response == '3':
            spotify_id = get_playlist_url("Spotify")
            break
        elif response == '4':
            youtube_id = get_playlist_url("YouTube")
            break
        else:
            print("Invalid response. Please enter '1', '2', '3', or '4'.")

    with open(full_file_path, 'w') as f:
        f.write(spotify_id + '\n')
        f.write(youtube_id + '\n')
    
    if songs_list_wipe:
        try:
            os.remove(os.path.join(script_dir, 'songs_added_list.json'))
        except FileNotFoundError:
            pass

    return spotify_id, youtube_id


##################### Interacting with the Spotify API #####################


def get_access_token(client_id, client_secret):
    '''
    Obtain an access token for authenticating requests to the Spotify API.

    Args:
    client_id (str): The client ID for your Spotify API app.
    client_secret (str): The client secret for your Spotify API app.

    Returns:
    str: The access token for authenticating requests to the Spotify API.
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
