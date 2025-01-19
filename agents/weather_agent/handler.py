import requests
from deep_translator import GoogleTranslator
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

def translate_location(location):
    """Translate location from Traditional Chinese to English."""
    try:
        translated_location = GoogleTranslator(source="zh-TW", target="en").translate(location)
        return translated_location
    except Exception as e:
        raise ValueError(f"無法翻譯地點名稱: {str(e)}")

def get_weather_info(data):
    """Fetch weather information using OpenWeather API."""
    location = data.get("location", "Taipei")  # 默認地點為台北

    try:
        # 翻譯地名
        translated_location = translate_location(location)
        
        # 發送請求到 OpenWeather API
        response = requests.get(
            OPENWEATHER_API_URL,
            params={
                "q": translated_location,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",  # 使用公制單位，返回攝氏溫度
                "lang": "zh_tw"    # 返回繁體中文
            }
        )
        response.raise_for_status()  # 如果請求失敗則拋出 HTTPError

        weather_data = response.json()
        description = weather_data["weather"][0]["description"]
        temperature = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]

        return {
            "response": f"{location}目前的天氣是{description}，溫度為{temperature}°C，濕度為{humidity}%。"
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"無法獲取天氣資訊: {str(e)}"}
    except ValueError as e:
        return {"error": str(e)}
