import youtube_api
import spotify_api
import re
import json
import os


def write_to_file():
    youtube = youtube_api.get_authenticated_service()
    tracks = spotify_api.spotify_track_lister()
    playlist_id = spotify_api.youtube_playlist_id
    filename = "song_log.json"
    existing_video_ids = youtube_api.yt_music_vid_ids(youtube, playlist_id)

    processed_songs = [re.sub(r"[.,!?\-_/ ()'\"]", "", song[0]).lower() for song in tracks]
    processed_keys = [re.sub(r"[.,!?\-_/ ()'\"]", "", key).lower() for key in existing_video_ids.keys()]

    # Load existing data
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    # Get the current count
    count = existing_data.get('count', 0) + 1

    # Update the data
    data = {
        f"video_titles_{count}": processed_keys,
        f"processed_songs_{count}": processed_songs,
        "count": count
    }

    # Merge with existing data
    existing_data.update(data)

    # Write the updated data
    with open(filename, 'w') as f:
        json.dump(existing_data, f)

    return count


def print_songs_and_titles(count):
    filename = "song_log.json"
    with open(filename, 'r') as f:
        data = json.load(f)
    
    video_titles = data[f"video_titles_{count}"]
    processed_songs = data[f"processed_songs_{count}"]
    
    max_length = max(len(processed_songs), len(video_titles))
    
    for i in range(max_length):
        song = processed_songs[i] if i < len(processed_songs) else "No song"
        title = video_titles[i] if i < len(video_titles) else "No title"
        print(f"{song:<40} {title}")


if __name__ == "__main__":
    try:
        count = write_to_file()  # Write to file and returns the count
        print("Finished writing to file")
        print_songs_and_titles(count)

    except Exception as e:
        if 'quota' in str(e):
            print("Quota exceeded. Please try again at 8AM GMT tomorrow.")
        else:
            print(f"An error occurred: {e}")
