import requests
import os
from dotenv import load_dotenv

script_dir = os.path.dirname(__file__)
load_dotenv(script_dir + "/../.env")
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

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
    