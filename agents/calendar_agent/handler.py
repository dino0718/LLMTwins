from langchain import OpenAI
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from datetime import datetime, timezone
import re

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def authenticate_google_calendar():
    """Authenticate with Google Calendar API."""
    creds = None
    token_path = "/home/ntc/dino/LLMTwins/tokens/token.json"
    credentials_path = "/home/ntc/dino/LLMTwins/tokens/credentials.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


def parse_user_input(query):
    """Use LLM to parse user input into structured data."""
    llm = OpenAI(temperature=0.7)
    current_year = datetime.now().year
    prompt = f"""
    你是一個日曆助手。用戶的輸入是: "{query}"。
    請解析以下內容並用 JSON 格式回應:
    {{
      "event_name": "<事件名稱>",
      "start_time": "<開始時間（ISO 8601 格式，如 {current_year}-01-20T09:00:00+08:00）>",
      "end_time": "<結束時間（ISO 8601 格式，如 {current_year}-01-20T12:00:00+08:00）>",
      "timezone": "Asia/Taipei"
    }}
    確保解析的日期和時間落在未來。
    """
    response = llm.generate(prompts=[prompt])
    try:
        parsed_data = eval(response.generations[0][0].text.strip())
    except Exception as e:
        return {"error": f"無法解析輸入: {e}"}
    return parsed_data


def create_google_calendar_event(data):
    """Create an event in Google Calendar based on parsed user input."""
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)

    # Parse user input
    query = data.get("query", "")
    parsed_data = parse_user_input(query)

    if "error" in parsed_data:
        return parsed_data

    # Validate and correct date
    parsed_data = validate_and_correct_date(parsed_data)

    # Validate ISO format
    if not validate_iso_format(parsed_data["start_time"]) or not validate_iso_format(
        parsed_data["end_time"]
    ):
        return {"error": "時間格式錯誤，請檢查輸入格式。"}

    # Prepare event data
    event = {
        "summary": parsed_data["event_name"],
        "start": {
            "dateTime": parsed_data["start_time"],
            "timeZone": parsed_data["timezone"],
        },
        "end": {
            "dateTime": parsed_data["end_time"],
            "timeZone": parsed_data["timezone"],
        },
    }

    # Create event
    try:
        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )
        return {"response": f"事件已建立: {created_event.get('htmlLink')}"}
    except Exception as e:
        return {"error": f"Google Calendar API 發送失敗: {e}"}


def validate_iso_format(time_string):
    """Validate if a given string is in ISO 8601 datetime format."""
    iso_format = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$"
    return re.match(iso_format, time_string) is not None


def validate_and_correct_date(parsed_data):
    """Validate and correct date if needed."""
    start_time = datetime.fromisoformat(parsed_data["start_time"])
    end_time = datetime.fromisoformat(parsed_data["end_time"])
    now = datetime.now(timezone.utc)  # 確保為 offset-aware datetime

    # 如果日期在過去，則自動補充為下一年
    if start_time < now:
        start_time = start_time.replace(year=now.year)
        end_time = end_time.replace(year=now.year)

    # 更新修正後的時間
    parsed_data["start_time"] = start_time.isoformat()
    parsed_data["end_time"] = end_time.isoformat()

    return parsed_data
