import os
import io
import logging
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

# Scopes required to read Drive metadata and download files
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveService:
    def __init__(self):
        self.credentials = self._get_credentials()
        if self.credentials:
            self.service = build('drive', 'v3', credentials=self.credentials)
        else:
            self.service = None
            logger.warning("Google Drive credentials not found. Drive Sync will be disabled.")

    def _get_credentials(self):
        """Load service account credentials from GOOGLE_APPLICATION_CREDENTIALS or local file."""
        # Check standard environment variable first
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")
        
        # If it's a relative path, resolve it relative to the backend directory
        if not os.path.isabs(cred_path):
            # Assumes this is run from the backend directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            cred_path = os.path.join(base_dir, cred_path)
            
        if os.path.exists(cred_path):
            try:
                return service_account.Credentials.from_service_account_file(
                    cred_path, scopes=SCOPES
                )
            except Exception as e:
                logger.error(f"Failed to load Google Drive credentials from {cred_path}: {e}")
                return None
        return None

    def sync_folder(self, folder_id: str, upload_dir: str) -> List[Dict[str, Any]]:
        """
        Lists files in a specific Drive folder, downloads them to the upload directory, 
        and returns a list of file metadata dictionaries to be ingested.
        """
        if not self.service:
            raise HTTPException(status_code=503, detail="Google Drive Service Account not configured.")

        # Ensure upload directory exists
        os.makedirs(upload_dir, exist_ok=True)
        
        synced_files = []
        page_token = None
        
        try:
            while True:
                # Build the query: files must be in the specified folder and not trashed
                query = f"'{folder_id}' in parents and trashed = false"
                
                # We specifically request mimeType to determine how to download (export or direct)
                response = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType, modifiedTime, owners, sharingUser)',
                    pageToken=page_token
                ).execute()

                for file in response.get('files', []):
                    try:
                        file_metadata = self._download_file(file, upload_dir)
                        if file_metadata:
                            synced_files.append(file_metadata)
                    except Exception as e:
                        logger.error(f"Failed to download/process Drive file {file.get('name')}: {e}")

                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
                    
            return synced_files

        except Exception as e:
            logger.error(f"Error syncing Drive folder {folder_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to sync Google Drive folder: {str(e)}")

    def _download_file(self, drive_file: dict, upload_dir: str) -> Optional[Dict[str, Any]]:
        """
        Downloads a single file from Google Drive based on its mimeType.
        Google Docs are exported as PDF or Text. Binary files are downloaded directly.
        """
        file_id = drive_file.get('id')
        file_name = drive_file.get('name')
        mime_type = drive_file.get('mimeType')
        modified_time = drive_file.get('modifiedTime')
        
        # Determine owner
        owners = drive_file.get('owners', [])
        owner_name = owners[0].get('displayName', 'Google Drive User') if owners else 'Google Drive User'

        # Mime type mappings for Google Workspace documents
        export_mime_types = {
            'application/vnd.google-apps.document': {
                'mime': 'text/plain', 
                'ext': '.txt'
            },
            'application/vnd.google-apps.presentation': {
                'mime': 'application/pdf', 
                'ext': '.pdf'
            },
            'application/vnd.google-apps.spreadsheet': {
                'mime': 'text/csv', 
                'ext': '.csv'
            }
        }

        # Unsupported google types (e.g. folders, shortcuts)
        if mime_type.startswith('application/vnd.google-apps.') and mime_type not in export_mime_types:
            logger.info(f"Skipping unsupported Google Workspace type: {file_name} ({mime_type})")
            return None

        # Clean filename to be safe for local file system
        safe_filename = "".join([c for c in file_name if c.isalpha() or c.isdigit() or c in ' .-_']).rstrip()
        
        if mime_type in export_mime_types:
            # It's a Google Doc/Sheet/Slide - requires export
            export_config = export_mime_types[mime_type]
            if not safe_filename.endswith(export_config['ext']):
                safe_filename += export_config['ext']
                
            local_path = os.path.join(upload_dir, f"{file_id}_{safe_filename}")
            request = self.service.files().export_media(fileId=file_id, mimeType=export_config['mime'])
        else:
            # It's a standard binary file (PDF, DOCX, TXT, etc.)
            local_path = os.path.join(upload_dir, f"{file_id}_{safe_filename}")
            request = self.service.files().get_media(fileId=file_id)

        # Execute download
        with io.FileIO(local_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
        logger.info(f"Successfully downloaded Google Drive file: {safe_filename} to {local_path}")

        # Return metadata ready for ingestion pipeline
        return {
            "title": file_name, # Original Drive name
            "file_path": local_path,
            "owner": owner_name,
            "modified_time": modified_time,
            "source": "google_drive",
            "drive_file_id": file_id
        }

# Singleton instance
google_drive_service = GoogleDriveService()
