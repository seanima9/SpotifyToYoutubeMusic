import spotify_api
import os
import time
from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')
client_secrets_json = os.getenv('YOUTUBE_CLIENT_SECRETS')

youtube = build('youtube', 'v3', developerKey=api_key)


def search_song(song_name, artist):
    '''
    Get YouTube video ID for a song

    Args:
    song_name (str): Name of the song
    artist (str): Name of the main artist

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


def get_authenticated_service():
    '''
    Get authenticated service for YouTube API uisng OAuth 2.0 to make API calls
    
    Returns:
    youtube (googleapiclient.discovery.Resource): Authenticated service for YouTube API
    '''
    scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_json, scopes)
    credentials = flow.run_local_server(port=0)

    return build('youtube', 'v3', credentials=credentials)


# TODO: Make function to make playlist


def add_song_to_playlist(youtube, playlist_id, video_id):
    youtube.playlistItems().insert(
        part="snippet",  # Part of the API to use
        body={
            'snippet': {  # Information about the video in here as dictionary
              'playlistId': playlist_id,  # ID of the playlist
              'resourceId': {  # Information about the video
                      'kind': 'youtube#video',  # Type of resource being added
                      'videoId': video_id  # ID of the video
                    }
            }
        }
    ).execute()


def main():
    youtube = get_authenticated_service()
    playlist_id = 'PLLa4kakNIOc6alYlkDqf8sYZdpi4s3Fow'  # My test playlist

    tracks = spotify_api.spotify_main()

    for song, artist in tracks:
        video_id = search_song(song, artist[0])
        if video_id:
            add_song_to_playlist(youtube, playlist_id, video_id)
            print(f"Added {song} by {artist} to the playlist.")
            time.sleep(0.05)
        else:
            print(f"Could not find YouTube video for {song} by {artist}")


if __name__ == '__main__':
    main()
