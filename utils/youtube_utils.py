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


def fetch_yt_playlist_contents(youtube, playlist_id):
    """
    Fetches the contents of a YouTube playlist, the video IDs and the playlist item IDs
    costs 1 unit per page, so with maxResults=50, it costs 1 unit per 50 videos
    we are assuming video titles have the song and artist in them

    Args:
    youtube (Resource): The authenticated YouTube API client
    playlist_id (str): The ID of the YouTube playlist

    Returns:
    dict: A dictionary mapping song and artist pairs to video IDs in the youtube music playlist currently
    dict: A dictionary mapping video IDs to playlist item IDs
    """
    existing_video_ids = {}
    video_to_playlist_item_ids = {}
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,  # Maximum number of results to return per page, can be between 1 and 50, cost is 1 unit per page
            pageToken=next_page_token,  
            fields="nextPageToken,items(id,snippet/title,snippet/resourceId/videoId)"
        )
        response = request.execute()
        # response is a dictionary looking like {'nextPageToken': '...', 'items': [{'snippet': {'resourceId': {'videoId': '...'}}}, ...]}

        for item in response.get('items', []):  # returns value of 'items' key if it exists, else returns an empty list
            video_title = item['snippet']['title']  # Will give the youtube video title
            video_id = item['snippet']['resourceId']['videoId']
            playlist_item_id = item['id']

            if video_id not in video_to_playlist_item_ids:
                video_to_playlist_item_ids[video_id] = [playlist_item_id]
            else:
                video_to_playlist_item_ids[video_id].append(playlist_item_id)

            existing_video_ids[video_title] = video_id 
        next_page_token = response.get('nextPageToken')  

        if not next_page_token:  # If there are no more pages
            break

    return existing_video_ids, video_to_playlist_item_ids
