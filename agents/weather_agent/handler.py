import requests
from deep_translator import GoogleTranslator
from langchain import OpenAI
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
load_dotenv()

# 環境變數和 API 配置
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# 設置日誌
logging.basicConfig(level=logging.INFO)


def parse_weather_query(query):
    """Parse natural language weather query into structured data."""
    llm = OpenAI(temperature=0.7)
    prompt = f"""
    你是一個貼心的天氣助手，專門幫助用戶解析天氣相關的問題。
    用戶的輸入是: "{query}"。
    請提取地點名稱和目標時間，格式為 JSON，例如:
    {{
        "location": "<地點名稱>",
        "datetime": "<目標時間 (YYYY-MM-DD HH:MM:SS)>"
    }}
    如果未指定時間，請設置為當前時間。
    """
    response = llm.generate(prompts=[prompt])
    try:
        parsed_data = eval(response.generations[0][0].text.strip())
        # 處理簡單的日期和時間修正（例如 1/24 下午3點）
        if "datetime" in parsed_data:
            parsed_data["datetime"] = normalize_datetime(parsed_data["datetime"])
        return parsed_data
    except Exception as e:
        logging.error(f"解析自然語言失敗: {e}")
        return {"location": "台北", "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

def normalize_datetime(raw_datetime):
    """Normalize raw datetime from LLM to standard format."""
    try:
        # 自然語言格式（例如 "1/24 下午3點"）轉換成標準時間
        if "下午" in raw_datetime or "上午" in raw_datetime:
            raw_datetime = raw_datetime.replace("下午", "PM").replace("上午", "AM")
        return datetime.strptime(raw_datetime, "%m/%d %p%I點").strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logging.error(f"日期格式解析失敗: {e}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    

def translate_location(location):
    """將地點名稱從繁體中文翻譯為英文。"""
    try:
        return GoogleTranslator(source="zh-TW", target="en").translate(location)
    except Exception as e:
        logging.warning(f"地點翻譯失敗，使用原始地點名稱: {location}，錯誤: {e}")
        return location  # 如果翻譯失敗，返回原始地點


def fetch_weather_forecast(location, target_date):
    """Fetch weather forecast for a specific date and time."""
    try:
        response = requests.get(
            OPENWEATHER_FORECAST_URL,
            params={
                "q": location,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "zh_tw"
            }
        )
        response.raise_for_status()
        forecast_data = response.json()

        # 解析目標日期
        target_datetime = datetime.strptime(target_date, "%Y-%m-%d %H:%M:%S")

        # 查找與目標時間最接近的預報
        closest_forecast = min(
            forecast_data["list"],
            key=lambda x: abs(datetime.strptime(x["dt_txt"], "%Y-%m-%d %H:%M:%S") - target_datetime)
        )

        return closest_forecast
    except requests.exceptions.RequestException as e:
        logging.error(f"天氣預報 API 請求失敗: {e}")
        return {"error": f"無法獲取天氣預報資訊: {e}"}
    except Exception as e:
        logging.error(f"處理天氣數據失敗: {e}")
        return {"error": "天氣數據解析失敗"}



def generate_weather_response(query, weather_data):
    """使用 LLM 生成自然語言天氣回覆。"""
    llm = OpenAI(temperature=0.7)
    prompt = f"""
    你是一個貼心的天氣助手，用戶剛查詢天氣。
    查詢內容: "{query}"
    天氣數據: {weather_data}

    請基於這些資訊生成簡潔且自然的回覆並在最後給使用者相對應天氣的提醒，例如:
    - "台北今天多雲，氣溫約25°C，濕度為70%，有幾趴的機率下雨。"
    - "明天台中的天氣是晴朗，最高溫為30°C，最低溫為22°C，有幾趴的機率下雨。"
    """
    response = llm.generate(prompts=[prompt])
    return response.generations[0][0].text.strip()


def handle_weather_request(data):
    """Handle user weather queries with time-specific forecasts."""
    query = data.get("query", "")
    if not query:
        return {"error": "請提供天氣查詢內容。"}

    # 第一步: 解析自然語言查詢
    parsed_data = parse_weather_query(query)
    location = parsed_data["location"]
    target_datetime = parsed_data["datetime"]

    # 第二步: 翻譯地點名稱
    translated_location = translate_location(location)

    # 第三步: 獲取天氣預報
    forecast = fetch_weather_forecast(translated_location, target_datetime)
    if "error" in forecast:
        return forecast

    # 提取天氣數據
    description = forecast["weather"][0]["description"]
    temperature = forecast["main"]["temp"]
    humidity = forecast["main"]["humidity"]
    forecast_time = forecast["dt_txt"]

    # 第四步: 生成自然語言回覆
    # 構建天氣數據字典
    weather_data = {
        "location": location,  # 地點名稱
        "forecast_time": forecast_time,  # 預報時間
        "description": description,  # 天氣描述
        "temperature": temperature,  # 氣溫
        "humidity": humidity  # 濕度
    }
    # 生成自然語言天氣回覆
    response = generate_weather_response(query, weather_data)
    return {"response": response}  # 返回回覆

