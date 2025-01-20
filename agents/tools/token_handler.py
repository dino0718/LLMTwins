from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# 路徑設置
CREDENTIALS_FILE = "/home/ntc/dino/LLMTwins/tokens/credentials.json"
TOKEN_FILE = "/home/ntc/dino/LLMTwins/tokens/token.json"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
]


def ensure_valid_token():
    """檢查並生成 Token，如果無效則重新生成"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        print("Token 無效或過期，正在重新生成...")
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
        print("新的 Token 已成功生成並保存至 token.json")
    else:
        print("Token 可用且有效")
    return creds


def get_sheets_service():
    """返回 Google Sheets API 客戶端"""
    creds = ensure_valid_token()
    service = build("sheets", "v4", credentials=creds)
    return service


def get_calendar_service():
    """返回 Google Calendar API 客戶端"""
    creds = ensure_valid_token()
    service = build("calendar", "v3", credentials=creds)
    return service
