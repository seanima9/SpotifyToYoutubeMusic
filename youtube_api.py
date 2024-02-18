import os
import time
import pickle
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import spotify_api
import log_test

# Load environment variables
load_dotenv()
client_secrets_json = os.getenv('YOUTUBE_CLIENT_SECRETS')


def normalize_title(title):
    '''
    Normalizes the title by removing keywords and punctuation.
    The title is converted to lowercase and returned.

    Args:
    title (str): The title to be normalized

    Returns:
    str: The normalized title
    '''
    keywords_pattern = r"\s*(feat\.?|fts\.?|ft\.?|featuring|with)\s*"
    punctuation_pattern = r"[.,$&!?’|@:\-_/ ()'\"]"

    step1 = re.sub(keywords_pattern, "", str(title), flags=re.IGNORECASE)
    step2 = re.sub(punctuation_pattern, "", step1, flags=re.IGNORECASE)

    return step2.lower()


def get_authenticated_service():
    '''
    Get authenticated service for YouTube API
    Stores the user's access and refresh tokens in a file called 'token.pickle'
    File is created automatically when the authorization flow completes for the first time

    Returns:
    youtube (googleapiclient.discovery.Resource): Authenticated service for YouTube API
    '''
    scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
    creds = None

    full_file_path = os.path.join(spotify_api.script_dir, 'token.pickle')
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.

    if os.path.exists(full_file_path):
        with open(full_file_path, 'rb') as token:
            creds = pickle.load(token)
            print()
            print("Loaded credentials from token.pickle")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh the token, no need to ask for permission again

        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_json, scopes)
            print('\n' +'-' * 50 )
            print("Starting local server for authentication...")
            print('-' * 50 + '\n')
            creds = flow.run_local_server(port=0)  # Open a web browser to authenticate the user

        # Save the credentials for the next run
        with open(full_file_path, 'wb') as token:
            pickle.dump(creds, token)
            print()
            print("Saved credentials to token.pickle")

    return build('youtube', 'v3', credentials=creds)


def search_song(youtube, song_name, artist):
    '''
    Get YouTube video ID for a song using name and artist
    Costs 100 units per request, so maxResults=1 costs 100 units

    Args:
    youtube (Resource): The authenticated YouTube API client
    song_name (str): The name of the song
    artist (str): The artist of the song

    Returns:
    video_id (str): YouTube video ID for the song, e.g. '2SUwOgmvzK4' or None if no video found
    '''
    request = youtube.search().list(
        q=f"{song_name} {artist}",  # Search query
        part="snippet",  # Part of the API to use
        maxResults=1,  # Number of results to return
        type="video",  # Type of result to return
        fields="items(id/videoId)",  # Fields to return
    )
    response = request.execute()

    if response['items']:
        return response['items'][0]['id']['videoId']
    return None


def add_song_to_playlist(youtube, playlist_id, video_id):
    '''
    Add a song to a YouTube playlist, costs 50 units per request
    '''
    youtube.playlistItems().insert(
        part="snippet",  # Part of the API to use
        body={
            'snippet': {  # Information about the video in here as dictionary
              'playlistId': playlist_id,
              'resourceId': {  # Information about the video
                      'kind': 'youtube#video',
                      'videoId': video_id
                    }
            }
        }
    ).execute()


def yt_music_vid_ids(youtube, playlist_id):
    """
    Fetch all video IDs in a given YouTube playlist and return a dictionary mapping song and artist pairs to video IDs
    e.g. {'song - artist': '2SUwOgmvzK4', ...}
    costs 1 unit per page, so with maxResults=50, it costs 1 unit per 50 videos
    we are assuming video titles have the song and artist in them

    Args:
    youtube (Resource): The authenticated YouTube API client
    playlist_id (str): The ID of the YouTube playlist

    Returns:
    dict: A dictionary mapping song and artist pairs to video IDs in the youtube music playlist currently
    """
    existing_video_ids = {}
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,  # Maximum number of results to return per page, can be between 1 and 50, cost is 1 unit per page
            pageToken=next_page_token,  
            fields="nextPageToken,items(snippet/title,snippet/resourceId/videoId)"
        )
        response = request.execute()
        # response is a dictionary looking like {'nextPageToken': '...', 'items': [{'snippet': {'resourceId': {'videoId': '...'}}}, ...]}

        for item in response.get('items', []):  # returns value of 'items' key if it exists, else returns an empty list
            video_title = item['snippet']['title']  # Will give the youtube video title
            video_id = item['snippet']['resourceId']['videoId']
            existing_video_ids[video_title] = video_id 
        next_page_token = response.get('nextPageToken')  

        if not next_page_token:  # If there are no more pages
            break

    return existing_video_ids


def song_adder(youtube):
    '''
    Add songs to a YouTube playlist
    Will not add songs that are already in the playlist, songs that could not be found on YouTube
    or songs that have the same name but different artists
    Will retry adding a song up to 'possible_tries' times if it fails

    Costs per request for each function used in this function:
    - search_song: 100 units per request, so maxResults=1 costs 100 units
    - add_song_to_playlist: 50 units per request
    - yt_music_vid_ids: 1 unit per page, so with maxResults=50, it costs 1 unit per 50 videos

    Args:
    youtube (Resource): The authenticated YouTube API client

    Returns:
    None
    '''
    playlist_id = spotify_api.youtube_playlist_id  # The ID of the YouTube playlist
    tracks = spotify_api.spotify_track_lister()  # tracks is a list of tuples containing the track name and a list of artists
    possible_tries = 3
    # A dictionary mapping song and artist pairs to video IDs in the youtube music playlist currently
    existing_video_ids = yt_music_vid_ids(youtube, playlist_id)  # 1 unit per 50 videos

    for song, artist in tracks:
        # Remove special characters and convert to lowercase
        song_processed = normalize_title(song)
        if any(song_processed in normalize_title(key) for key in existing_video_ids):
            print(f"{song}  is already in the playlist.")
            continue  # Move on to next song
        
        video_id = search_song(youtube, song, artist)  # 100 units per request
        if not video_id:
            print(f"Could not find YouTube video for {song} by {artist}")
            continue  # Move on to next song
        
        for attempt in range(possible_tries):  # Try adding the song up to 'possible_tries' times
            try:
                add_song_to_playlist(youtube, playlist_id, video_id)  # 50 units per request
                print(f"Added {song} by {artist} to the playlist.")
                break  # If successful, break out of the for attempt loop

            except Exception as e:
                print(f"Failed to add {song} by {artist} to the playlist. On attempt {attempt + 1} of {possible_tries}")
                print('-' * 50)
                print(f"Error message: {e}")
                print('-' * 50)

                if attempt < possible_tries - 1:
                    sleep_time = 4 * (attempt + 1)
                    print(f"Retrying in {sleep_time} seconds...")
                    print()
                    time.sleep(sleep_time)  # Wait before trying again
                else:
                    print("Failed to add song to playlist. Please try again later.")
                    return  # Stop the program


def main():
    try:
        youtube = get_authenticated_service()
    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        return
    
    print("\n" + "-" * 50)
    print("Authentication successful.")
    print('-' * 50 + "\n")

    try:
        song_adder(youtube)

    except Exception as e:
        if 'quota' in str(e):
            print("Quota exceeded. Please try again at 8AM GMT tomorrow.")
        else:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
