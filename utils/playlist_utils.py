import os
import re

script_dir = os.path.dirname(__file__)
if not os.path.exists(os.path.join(script_dir, '../data')):
    os.makedirs(os.path.join(script_dir, '../data'))
full_file_path = os.path.join(script_dir, '../data/playlist_ids.txt')


def normalize_title(title):
    '''
    Normalizes the title by removing keywords and punctuation, then returning the title in lowercase.

    Args:
    title (str): The title to be normalized

    Returns:
    str: The normalized title
    '''
    keywords_pattern = r"\s*(feat\.?|fts\.?|ft\.?|featuring|with)\s*"
    punctuation_pattern = r"[.,$&!?’|@:\-_/()'\[\]{}\"]"  # Space removed

    step1 = re.sub(keywords_pattern, "", str(title), flags=re.IGNORECASE)
    step2 = re.sub(punctuation_pattern, "", step1, flags=re.IGNORECASE)

    return step2.lower()


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