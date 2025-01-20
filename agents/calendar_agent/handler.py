from agents.tools.token_handler import get_calendar_service


def create_event(data):
    """建立日曆事件"""
    service = get_calendar_service()
    event = {
        "summary": data.get("summary", "未命名事件"),
        "start": {
            "dateTime": data.get("start_time"),
            "timeZone": data.get("timezone", "Asia/Taipei"),
        },
        "end": {
            "dateTime": data.get("end_time"),
            "timeZone": data.get("timezone", "Asia/Taipei"),
        },
    }

    try:
        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )
        return {"response": f"事件已建立: {created_event.get('htmlLink')}"}
    except Exception as e:
        return {"error": f"無法建立事件：{str(e)}"}
