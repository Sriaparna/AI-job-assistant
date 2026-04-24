import os.path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# The ID of your spreadsheet (Get this from the URL)
SPREADSHEET_ID = '1564pqjLxC7QDXi6_M72ibx2AWn38hHE69BrNaupaDao' 

def append_job_to_sheet(job_details):
    """
    job_details should be a list: [Title, Company, Score, Link]
    """
    if not os.path.exists('token.json'):
        return "Error: token.json not found. Run authentication first."

    creds = Credentials.from_authorized_user_file('token.json')
    service = build('sheets', 'v4', credentials=creds)

    # Prepare the data to be added as a new row
    body = {'values': [job_details]}
    
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A1", # It will find the next empty row automatically
        valueInputOption="RAW",
        body=body
    ).execute()
    
    print(f"✅ Job added to Google Sheet!")

if __name__ == "__main__":
    # Test adding a fake job
    test_data = ["Data Scientist", "Google", "9.5", "https://linkedin.com/test"]
    append_job_to_sheet(test_data)