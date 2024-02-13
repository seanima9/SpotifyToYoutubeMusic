import os
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
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
    Add songs from Spotify to a YouTube playlist, does not add songs that are already in the playlist

    Args:
    youtube (Resource): The authenticated YouTube API client

    Returns:
    None
    '''
    playlist_id = 'PLLa4kakNIOc6MG7wtPmQuAw4n_bHmkp-T'
    existing_video_ids = yt_music_vid_ids(youtube, playlist_id)
    tracks = spotify_api.spotify_track_lister()

    for song, artist in tracks:
        video_id = search_song(song, artist[0])

        if not video_id:
            print(f"Could not find YouTube video for {song} by {artist}")
            continue  # Skip to the next iteration if no video ID was found

        if video_id in existing_video_ids:
            print(f"{song} by {artist} is already in the playlist.")
            continue

        add_song_to_playlist(youtube, playlist_id, video_id)
        print(f"Added {song} by {artist} to the playlist.")
        time.sleep(0.05)


def main():
    youtube = get_authenticated_service()
    song_adder(youtube)


if __name__ == '__main__':
    main()
