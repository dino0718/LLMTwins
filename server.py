import os
from fastapi import FastAPI, HTTPException, Request
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from dotenv import load_dotenv
from agents.accounting_agent.handler import handle_command as handle_accounting
from agents.calendar_agent.handler import handle_command_calendar, find_event_id
from agents.weather_agent.handler import handle_weather_request

# 加載 .env 檔案中的環境變數
load_dotenv()

# 確保 OpenAI API Key 已載入
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("未找到 OPENAI_API_KEY，請確認 .env 文件設置是否正確！")

app = FastAPI()

# 初始化 LangChain LLM
llm = OpenAI(temperature=0.7)

prompt_template = PromptTemplate(
    input_variables=["user_input"],
    template="""
你是一個專業的 API 輔助助手，將用戶輸入的自然語言解析為結構化 API 請求。
用戶輸入: "{user_input}"

生成 JSON：
{{
    "agent_type": "<accounting|calendar|weather>",
    "command": "<query|add|update|delete>",
    "parameters": {{
        "summary": "<事件主題>",
        "start_time": "<開始時間 (ISO 8601)>",
        "end_time": "<結束時間 (ISO 8601)>",
        "timezone": "Asia/Taipei"
    }}
}}
""",
)


# 自然語言解析函數
def parse_user_input_to_api_request(user_input):
    try:
        response = llm(prompt_template.format(user_input=user_input))
        parsed_data = eval(response)

        # 如果是刪除事件，必須查詢 `event_id`
        if parsed_data["command"] == "delete":
            # 執行查詢，找到匹配的事件 ID
            event_id = find_event_id(
                summary=parsed_data["parameters"].get("summary"),
                start_time=parsed_data["parameters"].get("start_time"),
                end_time=parsed_data["parameters"].get("end_time"),
            )
            if event_id:
                parsed_data["parameters"]["event_id"] = event_id
            else:
                return {"error": "未找到匹配的事件，無法刪除"}

        return parsed_data
    except Exception as e:
        return {"error": f"解析失敗: {str(e)}"}


@app.post("/api/life-assistant")
async def unified_agent(request: Request):
    try:
        body = await request.json()
        natural_language = body.get("natural_language", False)
        user_input = body.get("query")

        if natural_language and user_input:
            # 使用自然語言解析
            structured_request = parse_user_input_to_api_request(user_input)
            if "error" in structured_request:
                raise HTTPException(status_code=400, detail=structured_request["error"])
        else:
            # 若為結構化請求，直接使用
            structured_request = body

        agent_type = structured_request.get("agent_type")
        command = structured_request.get("command")
        parameters = structured_request.get("parameters", {})

        if agent_type == "accounting":
            return handle_accounting(command, parameters)
        elif agent_type == "calendar":
            return handle_command_calendar(command, parameters)
        elif agent_type == "weather":
            return handle_weather_request(parameters)
        else:
            raise HTTPException(status_code=400, detail="Unknown agent type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
