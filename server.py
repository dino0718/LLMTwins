import os
from fastapi import FastAPI, HTTPException, Request
from agents.calendar_agent.handler import handle_command_calendar
from agents.weather_agent.handler import handle_weather_request
from agents.accounting_agent.handler import handle_command

app = FastAPI()


@app.post("/api/life-assistant")
async def unified_agent(request: Request):
    try:
        body = await request.json()
        agent_type = body.get("agent_type")
        command = body.get("command")
        parameters = body.get("parameters", {})

        if agent_type == "accounting":
            # 處理會計代理
            result = handle_command(command, parameters)
            return {"response": result}
        elif agent_type == "calendar":
            # 處理日曆代理
            print(f"Received Calendar Request: {body}")  # 調試日誌
            response = handle_command_calendar(command, parameters)
            print(f"Calendar Response: {response}")  # 調試日誌
            return response
        elif agent_type == "weather":
            # 處理天氣代理
            response = handle_weather_request(body)
            if "error" in response:
                raise HTTPException(status_code=400, detail=response["error"])
            return response
        else:
            raise HTTPException(status_code=400, detail="Invalid agent type provided.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
