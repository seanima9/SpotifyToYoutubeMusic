import json
import os
import sys

script_dir = os.path.dirname(__file__)
sys.path.append(f'{script_dir}/..')
if not os.path.exists(os.path.join(script_dir, '../data')):
    os.makedirs(os.path.join(script_dir, '../data'))
test_file = os.path.join(script_dir, '../logs/song_log.json')

from auth.youtube_auth import get_authenticated_service
from utils.playlist_utils import normalize_title, update_playlist_ids
from utils.youtube_utils import fetch_yt_playlist_contents
from services.spotify_services import spotify_track_lister


def create_missing_songs_dict():
    '''
    Creates a dictionary of songs and titles that are missing from the YouTube playlist.
    Assumes that both playlists are in the same order and have the same songs. Used for testing purposes.

    Returns:
    dict: The dictionary of missing songs and titles
    '''
    spotify_playlist_id, youtube_playlist_id = update_playlist_ids()
    youtube = get_authenticated_service()
    tracks = spotify_track_lister(spotify_playlist_id)
    playlist_id = youtube_playlist_id
    existing_video_ids = fetch_yt_playlist_contents(youtube, playlist_id)[0]

    processed_songs = [normalize_title(track[0]) for track in tracks]
    processed_keys_list = []

    # Create a list of processed keys from the existing_video_ids dictionary removing duplicates
    for key in existing_video_ids.keys():
        processed_key = normalize_title(key)
        if processed_key not in processed_keys_list:
            processed_keys_list.append(processed_key)

    # Create a dictionary of missing songs and titles
    song_not_in_title_dict = {}
    for index, song in enumerate(processed_songs):
        song_words = song.split(" ")
        score = 0.0
        for word in song_words:  # for every word in your string
            if any(word in key for key in processed_keys_list):  # if it is in your bigger string increase score
                score += 1
        if score / len(song_words) != 1.0:  # If not all words in the song are in a title
            try:
                song_not_in_title_dict[song] = processed_keys_list[index]  # Add the song and title to the dictionary
            except IndexError:
                pass

    return song_not_in_title_dict


def write_to_file(song_not_in_title_dict):
    '''
    Writes the missing songs and titles to a JSON file.
    The file is named "song_log.json" and is written to the current working directory.
    The file is updated with the missing songs and titles each time this function is called.

    Args:
    song_not_in_title_dict (dict): The dictionary of missing songs and titles

    Returns:
    int: The count of the current missing songs and titles dictionary in the JSON file
    '''

    if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
        with open(test_file, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    count = existing_data.get('count', 0) + 1

    data = {
        f"missing_songs_and_titles_{count}": song_not_in_title_dict,
        "count": count
    }

    existing_data.update(data)

    with open(test_file, 'w') as f:
        json.dump(existing_data, f, indent=4)

    return count


def print_songs_and_titles(count):
    '''
    Prints the songs and titles that are missing from the YouTube playlist.
    The count parameter is used to access the correct dictionary in the JSON file.
    
    Args:
    count (int): The count of the current missing songs and titles dictionary in the JSON file

    Returns:
    None
    '''
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    missing_songs_and_titles = data.get(f"missing_songs_and_titles_{count}", {})
    for song, title in missing_songs_and_titles.items():
        print(f"{song:<40} {title}")


def main():
    try:
        song_not_in_title_dict = create_missing_songs_dict()
        count = write_to_file(song_not_in_title_dict)  # Write to file and returns the count
        print("Finished writing to file")
        print_songs_and_titles(count)

    except Exception as e:
        if 'quota' in str(e):
            print("Quota exceeded. Please try again at 8AM GMT tomorrow.")
        else:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
