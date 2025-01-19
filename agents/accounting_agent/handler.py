from langchain_community.llms import OpenAI
import os
from dotenv import load_dotenv
import openai

# 載入 .env 檔案
load_dotenv()

# 讀取 OpenAI API 金鑰
openai.api_key = os.getenv('OPENAI_API_KEY')

def handle_accounting_request(data):
    """Handles accounting-related tasks."""
    query = data.get("query", "")
    if not query:
        return {"error": "缺少 query 參數"}

    llm = OpenAI(temperature=0.7)
    response = llm.generate(prompts=[f"記帳問題: {query}"])
    return {"response": response.generations[0][0].text.strip()}