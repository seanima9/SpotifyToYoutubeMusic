import os
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
import spotify_api


# Load environment variables
load_dotenv()
client_secrets_json = os.getenv('YOUTUBE_CLIENT_SECRETS')

def get_authenticated_service():
    '''
    Get authenticated service for YouTube API

    Returns:
    youtube (googleapiclient.discovery.Resource): Authenticated service for YouTube API
    '''
    scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_json, scopes)
    print()
    print('-' * 50)
    print("Starting local server for authentication...")
    print('-' * 50)
    print()
    credentials = flow.run_local_server(port=0)

    return build('youtube', 'v3', credentials=credentials)


def search_song(youtube, song_name, artist):
    '''
    Get YouTube video ID for a song using name and artist

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
    Fetch all video IDs in a given YouTube playlist

    Args:
    youtube (Resource): The authenticated YouTube API client
    playlist_id (str): The ID of the YouTube playlist

    Returns:
    set: A set of video IDs in the youtube music playlist currently
    """
    existing_video_ids = set()
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,  # Maximum number of results to return per page
            pageToken=next_page_token,  
            fields="nextPageToken,items(snippet/resourceId/videoId)"
        )
        response = request.execute()  

        for item in response.get('items', []):
            existing_video_ids.add(item['snippet']['resourceId']['videoId'])
        next_page_token = response.get('nextPageToken')  

        if not next_page_token:  # If there are no more pages
            break

    return existing_video_ids


def song_adder(youtube):
    '''
    Add songs to a YouTube playlist
    Will not add songs that are already in the playlist or songs that could not be found on YouTube
    Will retry adding a song up to 'possible_tries' times if it fails

    Args:
    youtube (Resource): The authenticated YouTube API client

    Returns:
    None
    '''
    playlist_id = 'PLLa4kakNIOc6MG7wtPmQuAw4n_bHmkp-T'
    tracks = spotify_api.spotify_track_lister()  # tracks is a list of tuples containing the track name and a list of artists
    possible_tries = 3

    existing_video_ids = yt_music_vid_ids(youtube, playlist_id)

    for song, artist in tracks:
        video_id = search_song(youtube, song, artist)
        
        if not video_id:
            print(f"Could not find YouTube video for {song} by {artist}")
            continue  # Move on to next song

        if video_id in existing_video_ids:
            print(f"{song} by {artist} is already in the playlist.")
            continue  # Move on to next song
        

        for attempt in range(possible_tries):  # Try adding the song up to 'possible_tries' times
            try:
                add_song_to_playlist(youtube, playlist_id, video_id)
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
    
    print()
    print('-' * 50)
    print("Authentication successful.")
    print('-' * 50)
    print()

    try:
        song_adder(youtube)

    except Exception as e:
        if 'quota' in str(e):
            print("Quota exceeded. Please try again at 8AM GMT tomorrow.")
        else:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
