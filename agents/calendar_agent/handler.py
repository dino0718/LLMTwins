from agents.tools.token_handler import ensure_valid_token, get_calendar_service
from googleapiclient.errors import HttpError


def query_events(parameters):
    """查詢日曆事件，檢查時間格式"""
    try:
        ensure_valid_token()
        service = get_calendar_service()
        calendar_id = "primary"
        time_min = parameters.get("time_min")
        time_max = parameters.get("time_max")

        # 檢查 time_min 和 time_max 是否存在
        if not time_min or not time_max:
            return {"error": "time_min and time_max are required"}

        # 確保時間格式一致
        is_datetime_format = "T" in time_min and "T" in time_max
        is_date_format = "T" not in time_min and "T" not in time_max

        if not (is_datetime_format or is_date_format):
            return {
                "error": "time_min and time_max must either both be date or both be dateTime"
            }

        # 查詢事件
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        return (
            events if events else {"message": "No events found in the specified range"}
        )
    except HttpError as error:
        return {"error": f"Google Calendar API Error: {error}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def create_event(data):
    """新增日曆事件，檢查時間格式一致性"""
    try:
        ensure_valid_token()
        service = get_calendar_service()

        # 確認時間格式一致
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if not start_time or not end_time:
            return {"error": "start_time and end_time are required"}

        is_datetime_format = "T" in start_time and "T" in end_time
        is_date_format = "T" not in start_time and "T" not in end_time

        if not (is_datetime_format or is_date_format):
            return {
                "error": "start_time and end_time must either both be date or both be dateTime"
            }

        # 創建事件
        event = {
            "summary": data.get("summary", "未命名事件"),
            "start": {
                "dateTime": start_time if is_datetime_format else None,
                "date": start_time if is_date_format else None,
                "timeZone": data.get("timezone", "Asia/Taipei"),
            },
            "end": {
                "dateTime": end_time if is_datetime_format else None,
                "date": end_time if is_date_format else None,
                "timeZone": data.get("timezone", "Asia/Taipei"),
            },
        }

        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )
        return {"response": f"事件已建立: {created_event.get('htmlLink')}"}
    except HttpError as error:
        return {"error": f"Google Calendar API Error: {error}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def update_event(parameters):
    """更新日曆事件"""
    try:
        ensure_valid_token()
        service = get_calendar_service()
        event_id = parameters.get("event_id")
        updated_event = (
            service.events().get(calendarId="primary", eventId=event_id).execute()
        )

        # 更新事件內容
        updated_event["summary"] = parameters.get("summary", updated_event["summary"])
        updated_event["start"]["dateTime"] = parameters.get(
            "start_time", updated_event["start"]["dateTime"]
        )
        updated_event["end"]["dateTime"] = parameters.get(
            "end_time", updated_event["end"]["dateTime"]
        )
        updated_event["start"]["timeZone"] = parameters.get(
            "timezone", updated_event["start"].get("timeZone", "Asia/Taipei")
        )
        updated_event["end"]["timeZone"] = parameters.get(
            "timezone", updated_event["end"].get("timeZone", "Asia/Taipei")
        )

        service.events().update(
            calendarId="primary", eventId=event_id, body=updated_event
        ).execute()
        return {"status": "success", "message": "Event updated successfully"}
    except HttpError as error:
        return {"error": f"Google Calendar API Error: {error}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def delete_event(parameters):
    """刪除日曆事件"""
    try:
        ensure_valid_token()
        service = get_calendar_service()
        event_id = parameters.get("event_id")

        if not event_id:
            return {"error": "event_id is required to delete an event"}

        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"status": "success", "message": "Event deleted successfully"}
    except HttpError as error:
        return {"error": f"Google Calendar API Error: {error}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def handle_command_calendar(command, parameters):
    print(f"Command: {command}, Parameters: {parameters}")  # 調試日誌
    if command == "query":
        if "time_min" not in parameters or "time_max" not in parameters:
            return {"error": "time_min and time_max are required for querying events"}
        return query_events(parameters)
    elif command == "add":
        if "start_time" not in parameters or "end_time" not in parameters:
            return {"error": "start_time and end_time are required for adding an event"}
        return create_event(parameters)
    elif command == "update":
        if "event_id" not in parameters:
            return {"error": "event_id is required for updating an event"}
        return update_event(parameters)
    elif command == "delete":
        if "event_id" not in parameters:
            return {"error": "event_id is required for deleting an event"}
        return delete_event(parameters)
    else:
        return {"error": "Unknown command"}
