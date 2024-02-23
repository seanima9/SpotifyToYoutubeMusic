# Playlist Sync Tool 🚀

The Playlist Sync Tool is a Python application designed to synchronize songs between Spotify and YouTube playlists. It offers functionalities to extract playlist IDs, authenticate with Spotify and YouTube APIs, add songs from Spotify to a YouTube playlist, and remove duplicate entries from the YouTube playlist.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.6 or higher
- pip for installing Python packages

### Installation

1. Clone the repository or download the source code.
2. Navigate to the project directory and install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables by creating a `.env` file in the project root with the following contents:
   ```env
   SPOTIFY_CLIENT_ID='your_spotify_client_id'
   SPOTIFY_CLIENT_SECRET='your_spotify_client_secret'
   YOUTUBE_CLIENT_SECRETS='path_to_your_youtube_client_secrets.json'
   ```
   Replace `'your_spotify_client_id'`, `'your_spotify_client_secret'`, and `'path_to_your_youtube_client_secrets.json'` with your actual credentials.

## API Setup

### Spotify API

1. Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and log in or create an account.
2. Create an application to obtain the Client ID and Client Secret.
3. Add these credentials to your `.env` file as shown in the Installation section.

### YouTube API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Navigate to APIs & Services > Credentials and click on Create Credentials > OAuth client ID.
4. Follow the prompts to configure the OAuth consent screen, selecting Desktop app as the application type.
5. Download the JSON file containing your credentials and note the file path.
6. Add the path to your `.env` file as `YOUTUBE_CLIENT_SECRETS`.

## Usage

1. Run the main script to start the program:
   ```bash
   python youtube_api.py
   ```
2. Follow the on-screen prompts to authenticate and choose between removing duplicates from your YouTube playlist or adding songs from Spotify to YouTube.
3. Add your playlist ids by following the prompts and copy and pasting your full URL when on each respective playlist

## Features

- **Playlist ID Extraction:** Automatically extracts and updates playlist IDs based on URLs.
- **Spotify Authentication:** Uses the Spotify Web API to fetch tracks from a Spotify playlist.
- **YouTube Authentication:** Authenticates with the YouTube API to add songs to a YouTube playlist and remove duplicates.
- **Song Synchronization:** Adds tracks from a Spotify playlist to a YouTube playlist, with checks to avoid duplicates.
- **Duplicate Removal:** Identifies and removes duplicate songs from a YouTube playlist.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs, questions, or new features.