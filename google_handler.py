import os
import pickle
import streamlit as st

class GoogleHandler:
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/spreadsheets'
    ]

    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        # Lazy imports to prevent boot crash
        from google.oauth2 import service_account
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        self.creds = None
        
        # 1. Try Streamlit Secrets (Service Account)
        if "gcp_service_account" in st.secrets:
            try:
                service_account_info = st.secrets["gcp_service_account"]
                self.creds = service_account.Credentials.from_service_account_info(
                    service_account_info, scopes=self.SCOPES
                )
                # Build services immediately
                self.drive_service = build('drive', 'v3', credentials=self.creds)
                self.sheets_service = build('sheets', 'v4', credentials=self.creds)
                return
            except Exception as e:
                print(f"Failed to load service account from secrets: {e}")

        # 2. Try Local Token (Backward Compatibility)
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # 3. Validate/Refresh Local Token or run Flow
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Flow is only possible in local environment (HEADLESS check)
                if not os.path.exists(credentials_file):
                     # If we are here, we failed all methods.
                     # Raise a specific error that the app can catch.
                     raise FileNotFoundError("Google Credentials not found. Please configure 'gcp_service_account' in Streamlit Secrets or provide 'credentials.json' locally.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save token for next run (only if using Flow/User auth)
            with open(token_file, 'wb') as token:
                pickle.dump(self.creds, token)

        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)

    def upload_file(self, file_content, file_name, folder_id=None):
        """Uploads a file to Google Drive."""
        try:
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create a temporary file to upload
            import io
            from googleapiclient.http import MediaIoBaseUpload
            
            media = MediaIoBaseUpload(io.BytesIO(file_content.encode('utf-8')), mimetype='application/pdf', resumable=True)
            
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
            print(f"File ID: {file.get('id')}")
            return file.get('webViewLink')
        except Exception as e:
            print(f"An error occurred during upload: {e}")
            return None

    def log_job(self, job_data, spreadsheet_id):
        """Logs job details to Google Sheets."""
        try:
            # Data to append
            values = [[
                job_data.get('date', ''),
                job_data.get('company', ''),
                job_data.get('title', ''),
                job_data.get('link', ''),
                job_data.get('status', 'Applied'),
                job_data.get('cv_link', ''),
                job_data.get('cover_letter_link', '')
            ]]
            
            body = {'values': values}
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range="Sheet1!A1",
                valueInputOption="USER_ENTERED", body=body).execute()
            
            print(f"{result.get('updates').get('updatedCells')} cells updated.")
            return True
        except Exception as e:
            print(f"An error occurred during logging: {e}")
            return False

    def create_sheet(self, title="Job Applications"):
        """Creates a new Google Sheet and returns its ID."""
        try:
            spreadsheet = {'properties': {'title': title}}
            spreadsheet = self.sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
            print(f"Spreadsheet ID: {spreadsheet.get('spreadsheetId')}")
            
            # Add headers
            headers = [['Date', 'Company', 'Title', 'Job Link', 'Status', 'CV Link', 'Cover Letter Link']]
            body = {'values': headers}
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet.get('spreadsheetId'), range="Sheet1!A1",
                valueInputOption="USER_ENTERED", body=body).execute()
                
            return spreadsheet.get('spreadsheetId')
        except Exception as e:
            print(f"Error creating sheet: {e}")
            return None
