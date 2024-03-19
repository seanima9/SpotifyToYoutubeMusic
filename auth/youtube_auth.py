import os
import pickle
from dotenv import load_dotenv
import logging

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

script_dir = os.path.dirname(__file__)
if not os.path.exists(os.path.join(script_dir, '../data')):
    os.makedirs(os.path.join(script_dir, '../data'))

pickle_path = os.path.join(script_dir, '../data/token.pickle')

env_path = os.path.join(script_dir, '../.env')
load_dotenv(env_path)
client_secrets_json = os.getenv('YOUTUBE_CLIENT_SECRETS')


def get_authenticated_service():
    '''
    Get authenticated service for YouTube API
    Stores the user's access and refresh tokens in a file called 'token.pickle'
    File is created automatically when the authorization flow completes for the first time

    Returns:
    youtube (googleapiclient.discovery.Resource): Authenticated service for YouTube API
    '''
    scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.

    if os.path.exists(pickle_path):
        with open(pickle_path, 'rb') as token:
            creds = pickle.load(token)
            print()
            print("Loaded credentials from token.pickle")

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # Refresh the token, no need to ask for permission again
            except Exception as e:
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_json, scopes)
            print('\n' +'-' * 50 )
            print("Starting local server for authentication...")
            print('-' * 50 + '\n')
            creds = flow.run_local_server(port=0)  # Open a web browser to authenticate the user

        # Save the credentials for the next run
        with open(pickle_path, 'wb') as token:
            pickle.dump(creds, token)
            print()
            print("Saved credentials to token.pickle")

    return build('youtube', 'v3', credentials=creds, cache_discovery=False)
