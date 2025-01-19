import re
from datetime import datetime, timedelta


def parse_expense(query):
    """解析用戶的記帳輸入"""
    patterns = {
        "amount": r"(\d+)[元$]",  # 金額
        "category": r"(早餐|午餐|晚餐|交通|娛樂|購物|其他)",  # 類別
        "date": r"(今天|昨天|\d{4}-\d{2}-\d{2})",  # 日期
    }

    # 提取金額
    amount = re.search(patterns["amount"], query)
    amount = int(amount.group(1)) if amount else None

    # 提取類別
    category = re.search(patterns["category"], query)
    category = category.group(1) if category else "其他"

    # 提取日期
    date = re.search(patterns["date"], query)
    if date:
        date = date.group(1)
        if date == "今天":
            date = datetime.now().strftime("%Y-%m-%d")
        elif date == "昨天":
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        date = datetime.now().strftime("%Y-%m-%d")

    return {"date": date, "category": category, "amount": amount, "note": ""}
