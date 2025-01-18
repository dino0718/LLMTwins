import os
from fastapi import FastAPI, HTTPException, Request
from agents.accounting_agent.handler import handle_accounting_request
from agents.calendar_agent.handler import create_google_calendar_event
from agents.weather_agent.handler import get_weather_info

app = FastAPI()

# Accounting Agent Route
@app.post("/api/accounting")
async def accounting_agent(request: Request):
    data = await request.json()
    response = handle_accounting_request(data)
    return response

# Calendar Agent Route
@app.post("/api/calendar")
async def calendar_agent(request: Request):
    data = await request.json()
    try:
        response = create_google_calendar_event(data)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"請求錯誤: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

@app.post("/api/weather")
async def weather_agent(request: Request):
    data = await request.json()
    try:
        response = get_weather_info(data)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
