import os
import time
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from main.utils import progress_message
import re
from googleapiclient.errors import HttpError
import asyncio

# Use a lock to ensure only one clone operation runs at a time
clone_lock = asyncio.Lock()
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Function to authenticate Google Drive
def authenticate_google_drive():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Authenticate and create the Drive service
creds = authenticate_google_drive()
drive_service = build('drive', 'v3', credentials=creds)

async def upload_to_google_drive(file_path, file_name, sts):
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, resumable=True)
    request = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink')

    response = None
    start_time = time.time()
    while response is None:
        status, response = request.next_chunk()
        if status:
            await progress_message(status.resumable_progress, os.path.getsize(file_path), "Uploading to Google Drive", sts, start_time)

    return response.get('webViewLink')



#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#clone

def extract_id_from_url(url):
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else None

async def copy_file(file_id, new_folder_id):
    try:
        # Acquire the lock
        async with clone_lock:
            # Retrieve the file's metadata
            file = drive_service.files().get(fileId=file_id, fields='name').execute()
            file_name = file['name']

            # Check if a file with the same name exists in the destination folder
            query = f"name='{file_name}' and '{new_folder_id}' in parents and trashed=false"
            existing_files = drive_service.files().list(q=query, fields='files(id)').execute().get('files', [])

            if existing_files:
                # Return the ID of the first existing file found
                return {'id': existing_files[0]['id'], 'name': file_name, 'status': 'existing'}

            # Prepare the metadata for copying the file
            copied_file_metadata = {
                'name': file_name,
                'parents': [new_folder_id]
            }

            # Copy the file to the new folder
            copied_file = drive_service.files().copy(fileId=file_id, body=copied_file_metadata).execute()

            return {'id': copied_file['id'], 'name': file_name, 'status': 'new'}
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24

def get_files_in_folder(folder_id):
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        return results.get('files', [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
