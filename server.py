from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from models import  prompt

# Load environment variables from .env file
load_dotenv()
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health")
async def health():
    return {"result": "Healthy Server!"}

def self_introduction():
    return "我的名字叫做小明，我是一個 AI 聊天機器人，我可以幫助你進行自我介紹。"

self_intro_agent = Agent(
   name="Self-introduction Agent",
   role="自我介紹",
   tools=[self_introduction],
   show_tool_calls=True
)

def analyse_project():
    return "我是專案分析 Agent，我可以幫助你分析專案。"

analysis_project_agent = Agent(
   name="Project analysis Agent",
   role= "專案分析",
   tools=[analyse_project],
   show_tool_calls=True
)



# 新增股票代理功能
import yfinance as yf
def stock_analysis(stock_symbol: str):
    """
    使用 Yahoo Finance API 獲取股票資訊
    """
    try:
        stock = yf.Ticker(stock_symbol)
        stock_info = stock.info

        current_price = stock_info.get('currentPrice', 'N/A')
        currency = stock_info.get('currency', 'N/A')
        recommendation = stock_info.get('recommendationKey', 'N/A')

        if current_price == 'N/A':
            return f"無法獲取股票代碼 {stock_symbol} 的資訊，請檢查股票代碼。"

        return (
            f"股票代碼: {stock_symbol}\n"
            f"當前價格: {current_price} {currency}\n"
            f"建議操作: {recommendation}"
        )
    except Exception as e:
        return f"發生錯誤: {str(e)}"

# 新增 Stock Agent
stock_agent = Agent(
    name="Stock Analysis Agent",
    role="股票分析",
    tools=[stock_analysis],
    show_tool_calls=True
)


# Create agent team
agent_team = Agent(
    model=OpenAIChat(
        id = "gpt-4o",
        temperature = 1,
        timeout = 30
    ),
   name="Agent Team",
   team=[self_intro_agent, analysis_project_agent,stock_agent],
   add_history_to_messages=True,
   num_history_responses=3,
   show_tool_calls=False,
   tool_call_limit=1
)

@app.post("/prompt")
async def prompt(prompt: prompt):
    response = agent_team.run(f"{prompt.message}", stream=False)
    # 尋找 assistant role 的最後一條訊息
    assistant_content = None
    for message in response.messages:
        if message.role == "assistant" and message.content:
            assistant_content = message.content

    return {"result": True, "message": assistant_content}



###
# 新增 API 端點
from pydantic import BaseModel

class StockRequest(BaseModel):
    stock_symbol: str

@app.post("/stock")
async def stock_prompt(request: StockRequest):
    response = stock_agent.run(request.stock_symbol, stream=False)
    return {"result": True, "message": response}