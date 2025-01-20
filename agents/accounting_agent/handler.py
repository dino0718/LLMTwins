from googleapiclient.errors import HttpError
from agents.tools.token_handler import ensure_valid_token, get_sheets_service


# Google Sheet 設置
SPREADSHEET_ID = "13TmNPh4RsIPtZa7SqsQFkyi7vGxLgBhRSaOq34YedAI"  # 替換為實際的試算表 ID
SHEET_NAME = "記帳"  # 替換為你的工作表名稱


def query_entries(parameters):
    """查詢記帳條目"""
    try:
        ensure_valid_token()  # 確認 Token 是否有效
        service = get_sheets_service()
        range_ = f"{SHEET_NAME}!A:D"
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=range_)
            .execute()
        )
        rows = result.get("values", [])

        # 過濾條目
        date_range = parameters.get("date_range", None)
        category = parameters.get("category", None)
        filtered_rows = []

        for row in rows:
            # 確保行數據完整
            if len(row) < 2:
                continue

            # 移除空白字符
            row_date = row[0].strip()
            row_category = row[1].strip()

            # 日期篩選
            if date_range and not (date_range[0] <= row_date <= date_range[1]):
                continue

            # 分類篩選
            if category and row_category != category:
                continue

            filtered_rows.append(row)

        return filtered_rows
    except HttpError as error:
        return {"error": f"Google Sheets API Error: {error}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def add_entry(parameters):
    """新增記帳條目"""
    try:
        ensure_valid_token()  # 確認 Token 是否有效
        service = get_sheets_service()
        range_ = f"{SHEET_NAME}!A:D"
        values = [
            [
                parameters.get("date"),
                parameters.get("category"),
                parameters.get("amount"),
                parameters.get("description", ""),
            ]
        ]
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )
        return {
            "status": "success",
            "updated_cells": result.get("updates", {}).get("updatedCells", 0),
        }
    except HttpError as error:
        return {"error": f"Google Sheets API Error: {error}"}


def update_entry(parameters):
    """更新記帳條目"""
    try:
        ensure_valid_token()  # 確認 Token 是否有效
        service = get_sheets_service()
        range_ = f"{SHEET_NAME}!A:D"
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=range_)
            .execute()
        )
        rows = result.get("values", [])

        updated = False
        for i, row in enumerate(rows):
            if row[0] == parameters.get("date") and row[1] == parameters.get(
                "category"
            ):
                rows[i] = [
                    parameters.get("date"),
                    parameters.get("category"),
                    parameters.get("amount"),
                    parameters.get("description", ""),
                ]
                updated = True
                break

        if not updated:
            return {"error": "Entry not found for update"}

        body = {"values": rows}
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_,
            valueInputOption="RAW",
            body=body,
        ).execute()

        return {"status": "success", "message": "Entry updated successfully"}
    except HttpError as error:
        return {"error": f"Google Sheets API Error: {error}"}


def delete_entry(parameters):
    """刪除指定記帳條目整行"""
    try:
        ensure_valid_token()  # 確認 Token 是否有效
        service = get_sheets_service()
        range_ = f"{SHEET_NAME}!A:D"
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=range_)
            .execute()
        )
        rows = result.get("values", [])

        entry_found = False
        row_index_to_delete = None

        for i, row in enumerate(rows):
            # 確保行數據完整
            if len(row) < 2:
                continue

            # 移除空白字符並進行匹配
            row_date = row[0].strip()
            row_category = row[1].strip()
            if row_date == parameters.get("date") and row_category == parameters.get(
                "category"
            ):
                entry_found = True
                row_index_to_delete = i + 1  # Google Sheets 的行索引從 1 開始
                break

        if not entry_found:
            return {"error": "Entry not found for deletion"}

        # 使用 batchUpdate 刪除整行
        request_body = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": 0,  # 工作表 ID（通常默認為 0，若不是請根據情況調整）
                            "dimension": "ROWS",
                            "startIndex": row_index_to_delete
                            - 1,  # 刪除起始索引（0 基）
                            "endIndex": row_index_to_delete,  # 刪除結束索引（不含）
                        }
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=request_body,
        ).execute()

        return {"status": "success", "message": "Row deleted successfully"}
    except HttpError as error:
        return {"error": f"Google Sheets API Error: {error}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def handle_command(command, parameters):
    """根據命令執行相應操作"""
    if command == "query":
        return query_entries(parameters)
    elif command == "add":
        return add_entry(parameters)
    elif command == "update":
        return update_entry(parameters)
    elif command == "delete":
        return delete_entry(parameters)
    else:
        return {"error": "Unknown command"}
