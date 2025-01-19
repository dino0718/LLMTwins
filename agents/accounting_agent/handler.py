from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "13TmNPh4RsIPtZa7SqsQFkyi7vGxLgBhRSaOq34YedAI"  # 替換為你的 Sheet ID


def get_sheets_service():
    """初始化 Google Sheets API"""
    creds = Credentials.from_authorized_user_file(
        "/home/ntc/dino/LLMTwins/tokens/token.json", SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def add_expense(query):
    """新增記帳條目到 Google Sheets"""
    from .parser import parse_expense  # 延遲導入

    data = parse_expense(query)
    row = [[data["date"], data["category"], data["amount"], data["note"]]]

    service = get_sheets_service()
    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range="A1:D1",
        valueInputOption="USER_ENTERED",
        body={"values": row},
    ).execute()
    return {"response": f"成功新增記帳條目：{data}"}
