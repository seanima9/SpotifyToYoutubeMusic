import youtube_api
import spotify_api
import re
import json
import os


def create_missing_songs_dict():
    '''
    Creates a dictionary of songs and titles that are missing from the YouTube playlist.
    Assumes that both playlists are in the same order and have the same songs. Used for testing purposes.
    Returns:
    dict: The dictionary of missing songs and titles
    int: The count of the current missing songs and titles dictionary
    '''
    youtube = youtube_api.get_authenticated_service()
    tracks = spotify_api.spotify_track_lister()
    playlist_id = spotify_api.youtube_playlist_id
    existing_video_ids = youtube_api.yt_music_vid_ids(youtube, playlist_id)

    processed_songs = [youtube_api.normalize_title(track[0]) for track in tracks]
    processed_keys_list = []

    # Create a list of processed keys from the existing_video_ids dictionary removing duplicates
    for key in existing_video_ids.keys():
        processed_key = youtube_api.normalize_title(key)
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
    filename = "/home/seanimani/personal_projs/playlist_conv/song_log.json"

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    count = existing_data.get('count', 0) + 1

    data = {
        f"missing_songs_and_titles_{count}": song_not_in_title_dict,
        "count": count
    }

    existing_data.update(data)

    with open(filename, 'w') as f:
        json.dump(existing_data, f, indent=4)

    return count


def print_songs_and_titles(count):
    '''
    Prints the songs and titles that are missing from the YouTube playlist.
    The count parameter is used to access the correct dictionary in the JSON file.
    
    Args:
    count (int): The count of the current missing songs and titles dictionary in the JSON file
    '''
    filename = "/home/seanimani/personal_projs/playlist_conv/song_log.json"
    with open(filename, 'r') as f:
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
