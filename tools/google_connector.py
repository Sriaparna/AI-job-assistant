import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# This tells Google we want to edit Sheets and read Gmail
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/gmail.modify']

def authenticate():
    creds = None
    # Check if a login session (token) already exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there's no valid login, trigger the browser login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Look for the file you just downloaded
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("Error: 'credentials.json' not found in root folder.")
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the session so you don't have to log in every time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    print("✅ Success: Google Infrastructure Connected!")
    return creds

if __name__ == "__main__":
    authenticate()