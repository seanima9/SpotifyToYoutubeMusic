# Spotify to YouTube Playlist Synchronizer 🚀

This project synchronizes tracks from a Spotify playlist to a YouTube playlist, automatically adding new tracks from Spotify to YouTube without duplicating existing ones. It's built using Python and utilizes the Spotify Web API and YouTube Data API v3 for playlist management.

## Getting Started

These instructions will guide you through setting up and running the project on your local machine.

## Prerequisites

Python 3.6 or higher
pip for installing dependencies
A Spotify Developer account and a Google Developer account for API access

## Installation

Clone the repository

Install required Python packages with
pip install -r requirements.txt
Set up Spotify API access:

Go to the Spotify Developer Dashboard and create an app to get your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.
Set up YouTube API access:

Visit the Google Cloud Console, create a project, and enable the YouTube Data API v3.
Create OAuth 2.0 credentials to obtain the client_secret.json file. Download this file to your project directory.
Configure environment variables:


Fill in your Spotify and Google credentials in a .env file in the same dir:

SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
YOUTUBE_CLIENT_SECRETS=path/to/your/downloaded/client_secret.json

## Usage

Set Spotify Playlist ID and YouTube Playlist ID:

In spotify_api.py, set your Spotify playlist ID you want to copy tracks from.
In the song_adder function within main.py, set the YouTube playlist ID where you want to add songs.

Run the Application:

python main.py
Follow the on-screen instructions to authenticate with YouTube on your first run.
Synchronization:

The script will list tracks from the specified Spotify playlist and add them to the specified YouTube playlist, avoiding duplicates.
Be aware of the API quota limits set by Google and Spotify. Extensive use of the APIs may require you to request quota increases.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to suggest improvements or add new features.
