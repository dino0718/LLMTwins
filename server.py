import os
from fastapi import FastAPI, HTTPException, Request
from agents.calendar_agent.handler import create_event
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
async def calendar_create(request: Request):
    data = await request.json()
    response = create_event(data)
    return response


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


# @app.post("/api/accounting/query")
# async def query_expenses_route(request: Request):
#     """查詢記帳條目"""
#     data = await request.json()
#     date_range = data.get("date_range", None)
#     category = data.get("category", None)

#     try:
#         from agents.accounting_agent.handler import query_expenses

#         results = query_expenses(date_range=date_range, category=category)
#         return {"results": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")


# @app.post("/api/accounting/update")
# async def update_expenses_route(request: Request):
#     """更新記帳條目"""
#     data = await request.json()
#     date = data.get("date")
#     category = data.get("category")
#     new_data = data.get("new_data")

#     try:
#         from agents.accounting_agent.handler import update_expense

#         response = update_expense(date=date, category=category, new_data=new_data)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")


# @app.delete("/api/accounting/delete")
# async def delete_expenses_route(request: Request):
#     """刪除記帳條目"""
#     data = await request.json()
#     date = data.get("date")
#     category = data.get("category")

#     try:
#         from agents.accounting_agent.handler import delete_expense

#         response = delete_expense(date=date, category=category)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=5000)
