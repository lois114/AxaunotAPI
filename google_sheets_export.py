import gspread
import pandas as pd
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def export_to_google_sheets(spreadsheet_id: str, sheets: dict, credentials_file: str = "service-account.json"):
    credentials = Credentials.from_service_account_file(
        credentials_file,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(spreadsheet_id)

    for sheet_name, df in sheets.items():
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=50)

        # Conversion des dates pandas -> texte pour Google Sheets
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime("%Y-%m-%d")

        df = df.fillna("")

        data = [df.columns.tolist()] + df.values.tolist()

        worksheet.update(data)

    print(f"Google Sheets mis à jour : {spreadsheet_id}")
