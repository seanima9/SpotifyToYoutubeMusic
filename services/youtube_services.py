import os
import time
import sys
import logging
import json

script_dir = os.path.dirname(__file__)
sys.path.append(f'{script_dir}/..')
if not os.path.exists(os.path.join(script_dir, '../logs')):
    os.makedirs(os.path.join(script_dir, '../logs'))
log_file = os.path.join(script_dir, '../logs/youtube_services.log')
logging.basicConfig(level=logging.INFO, filename = log_file, filemode= 'w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

from auth.youtube_auth import get_authenticated_service

from utils.playlist_utils import normalize_title, update_playlist_ids
from utils.youtube_utils import search_song, fetch_yt_playlist_contents, add_song_to_playlist
from services.spotify_services import spotify_track_lister


def remove_duplicates(youtube, playlist_id):
    '''
    Removes duplicate songs from a YouTube playlist, costs 50 units per removal

    Args:
    youtube (Resource): The authenticated YouTube API client
    playlist_id (str): The ID of the YouTube playlist

    Returns:
    None
    '''
    video_to_playlist_item_ids = fetch_yt_playlist_contents(youtube, playlist_id)[1]  # 1 unit per 50 videos
    count_removed = 0
    for video_id, playlist_item_id in video_to_playlist_item_ids.items():
        if len(playlist_item_id) > 1:
            for item_id in playlist_item_id[1:]:
                youtube.playlistItems().delete(id=item_id).execute() # 50 units per request
                count_removed += 1
                logging.info(f"Removed duplicate song with video ID {video_id} from the playlist.")
    print("Duplicates removed. Total removed: ", count_removed)
    logging.info(f"Total removed: {count_removed}")
    return


def attempter(possible_tries, youtube, playlist_id, video_id, song, artist, songs_added_list):
    '''
    Retry adding a song to a YouTube playlist if it fails, costs 50 units
    
    Args:
    youtube (Resource): The authenticated YouTube API client
    playlist_id (str): The ID of the YouTube playlist
    video_id (str): The ID of the YouTube video
    song (str): The name of the song
    artist (str): The artist of the song

    Returns:
    None
    '''
    for attempt in range(possible_tries):
            try:
                add_song_to_playlist(youtube, playlist_id, video_id)  # 50 units per request
                logging.info(f"Added {song} by {artist} to the playlist.")
                print(f"Added {song} by {artist} to the playlist.")
                songs_added_list.append((song, artist))
                break

            except Exception as e:
                if 'quota' in str(e):
                    return
                else:
                    print(f"Failed to add {song} by {artist} to the playlist. On attempt {attempt + 1} of {possible_tries}")
                    print('-' * 50)
                    print(f"Error message: {e}")
                    logging.error(f"Failed to add {song} by {artist} to the playlist. On attempt {attempt + 1} of {possible_tries}")
                    print('-' * 50)

                    if attempt < possible_tries - 1:
                        sleep_time = 4 * (attempt + 1)
                        print(f"Retrying in {sleep_time} seconds...")
                        print()
                        time.sleep(sleep_time)  # Wait before trying again
                    else:
                        print("Failed to add song to playlist. Please try again later.")
                        return


def song_adder(youtube, playlist_id, tracks):
    '''
    Add songs to a YouTube playlist if they are not already in the playlist, costs 100 units per song
    Adds songs added to a list to prevent re-adding them upon re-running the program
    Works in tandem with song in playlist checker so first run may add duplicates second run will not

    Args:
    youtube (Resource): The authenticated YouTube API client
    playlist_id (str): The ID of the YouTube playlist
    tracks (list): A list of tuples containing song and artist pairs

    Returns:
    None
    '''
    existing_video_ids = fetch_yt_playlist_contents(youtube, playlist_id)[0]  # 1 unit per 50 videos
    processed_keys_list = [normalize_title(key) for key in existing_video_ids]
    count = 0
    chosen_count = None
    MAX_RETRIES = 3

    while not chosen_count:
        chosen_count = input("How many songs do you want to add to the playlist? (Beware of quota limits): ")
        if chosen_count.isdigit():
            chosen_count = int(chosen_count)
        else:
            print("Please enter a valid number.")
            chosen_count = None

    songs_add_list_path = os.path.join(script_dir, '../data/songs_added_list.json')
    try:
        with open(songs_add_list_path, 'r') as f:
            songs_added_list = json.load(f)
    except FileNotFoundError:
        songs_added_list = []

    for song, artist in tracks:
        if count == chosen_count:
            break
        if [song, artist] in songs_added_list:
            continue

        song_words = normalize_title(song).split(" ")
        score = 0.0
        for word in song_words:
            if any(word in key for key in processed_keys_list):
                score += 1
        if score / len(song_words) == 1.0:
            logging.info(f"{song}  is already in the playlist.")
            continue
        
        video_id = search_song(youtube, song, artist)  # 100 units per request
        if not video_id:
            print(f"Could not find YouTube video for {song} by {artist}")
            logging.error(f"Could not find YouTube video for {song} by {artist}")
            continue

        count += 1
        attempter(MAX_RETRIES, youtube, playlist_id, video_id, song, artist, songs_added_list)

    with open(songs_add_list_path, 'w') as f:
        json.dump(songs_added_list, f)

    print(f"Added {count} songs to the playlist.")


def manage_youtube_playlist():
    '''
    Tries authentication, then gets playlist IDs and asks user what they want to do
    '''
    try:
        youtube = get_authenticated_service()
    except Exception as e:
        logging.error(f"An error occurred during authentication: {e}")
        print(f"An error occurred during authentication: {e}")
        return
    
    print("\n" + "-" * 50)
    print("Authentication successful.")
    print('-' * 50 + "\n")

    # Get playlist IDs
    spotify_playlist_id, youtube_playlist_id = update_playlist_ids()

    choice = '1'
    while choice in ['1', '2']:
        choice = input("\nDo you want to \n"
                    "1: remove duplicates from the playlist? Or \n"
                    "2: add songs to the playlist from spotify? \n"
                    "Enter 1 or 2, or any other key to exit\n: ")
        
        try:
            if choice == '1':
                print("Removing duplicates from the playlist...")
                remove_duplicates(youtube, youtube_playlist_id)

            if choice == '2':
                print("\nLoading...\n")
                song_adder(youtube, youtube_playlist_id, spotify_track_lister(spotify_playlist_id))

        except Exception as e:
            if 'quota' in str(e):
                print("Quota exceeded. Please try again at 8AM GMT tomorrow.")
            else:
                print(f"An error occurred: {e}")
                logging.error(f"An error occurred: {e}")
                print("\nIf the problem persists, perhaps your playist ID is incorrect. Please check and try again.")

    print("\nClosing program. Bye!")
    return


if __name__ == '__main__':
    manage_youtube_playlist()