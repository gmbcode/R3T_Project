"""TMail Fetcher Library"""
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path

scopes = ["https://mail.google.com/"]
creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", scopes)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", scopes
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())
class GmailService:
    """Gmail Service Class"""
    def __init__(self):
        try:
            self.service = build("gmail", "v1", credentials=creds)

        except HttpError as error:
            self.service = None
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {str(error)}")

