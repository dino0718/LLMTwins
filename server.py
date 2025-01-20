import os
from fastapi import FastAPI, HTTPException, Request
from agents.calendar_agent.handler import handle_command_calendar
from agents.weather_agent.handler import handle_weather_request
from agents.accounting_agent.handler import handle_command

app = FastAPI()


# accounting agent route
@app.post("/api/sheet/operations")
async def sheet_operations(request: Request):
    try:
        body = await request.json()
        command = body.get("operation")
        parameters = body.get("parameters", {})
        result = handle_command(command, parameters)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


# Calendar Agent Route
@app.post("/api/calendar")
async def calendar_route(request: Request):
    try:
        data = await request.json()
        print(f"Received Calendar Request: {data}")  # 調試日誌
        command = data.get("command")
        parameters = data.get("parameters", {})
        response = handle_command_calendar(command, parameters)
        print(f"Calendar Response: {response}")  # 調試日誌
        return response
    except Exception as e:
        print(f"Error in /api/calendar: {str(e)}")  # 調試日誌
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@app.post("/api/weather")
async def weather_agent(request: Request):
    data = await request.json()
    try:
        response = handle_weather_request(data)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")
