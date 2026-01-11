import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from backend.services.credentials import ensure_credentials

# Load credentials from ~/.mondaybrew/.env (or local .env fallback)
ensure_credentials()


class GoogleSheetsService:
    def __init__(self):
        # Re-use the OAuth credentials from Google Ads if possible,
        # assuming the user granted Sheets scopes.
        self.creds = Credentials(
            token=None,
            refresh_token=os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_ADS_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )

        self.service = build("sheets", "v4", credentials=self.creds)
        self.drive = build("drive", "v3", credentials=self.creds)

    def read_sheet(self, spreadsheet_id, range_name):
        """Reads values from a specific range."""
        try:
            sheet = self.service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            values = result.get("values", [])
            return values
        except Exception as e:
            print(f"Error reading sheet: {e}")
            return None

    def write_sheet(self, spreadsheet_id, range_name, values):
        """Writes values to a specific range."""
        print(
            f"[Sheets] Writing {len(values)} rows to {spreadsheet_id} range {range_name}..."
        )
        try:
            body = {"values": values}
            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            print(f"[Sheets] Success! {result.get('updatedCells')} cells updated.")
            return result
        except Exception as e:
            print(f"[Sheets] Error writing to sheet: {e}")
            return None

    def clear_range(self, spreadsheet_id, range_name):
        """Clears values from a specific range."""
        print(f"[Sheets] Clearing range {range_name} in {spreadsheet_id}...")
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .clear(spreadsheetId=spreadsheet_id, range=range_name, body={})
                .execute()
            )
            print(f"[Sheets] Cleared range. {result.get('clearedRange')}")
            return result
        except Exception as e:
            print(f"[Sheets] Error clearing range: {e}")
            return None

    def create_spreadsheet(self, title):
        """Creates a new spreadsheet."""
        try:
            spreadsheet = {"properties": {"title": title}}
            spreadsheet = (
                self.service.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId")
                .execute()
            )
            print(f"Created spreadsheet ID: {spreadsheet.get('spreadsheetId')}")
            return spreadsheet.get("spreadsheetId")
        except Exception as e:
            print(f"Error creating spreadsheet: {e}")
            return None

    def copy_file(self, file_id, new_title, folder_id=None):
        """Copies a file (template) to a new location."""
        try:
            body = {"name": new_title}
            if folder_id:
                body["parents"] = [folder_id]

            new_file = self.drive.files().copy(fileId=file_id, body=body).execute()

            print(f"Copied file. New ID: {new_file.get('id')}")
            return new_file.get("id")
        except Exception as e:
            print(f"Error copying file: {e}")
            return None

    def upload_file(
        self,
        file_path,
        file_name,
        folder_id=None,
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ):
        """Uploads a file to Google Drive."""
        try:
            file_metadata = {"name": file_name}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            from googleapiclient.http import MediaFileUpload

            media = MediaFileUpload(file_path, mimetype=mime_type)

            file = (
                self.drive.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            print(f"File ID: {file.get('id')}")
            return file.get("id")
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None


if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv

    load_dotenv()
    # service = GoogleSheetsService()
    # print(service.read_sheet("YOUR_SHEET_ID", "Sheet1!A1:B2"))
