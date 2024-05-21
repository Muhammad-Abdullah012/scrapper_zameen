import re
from datetime import datetime, timedelta

mapping = {"Crore": 7, "Lakh": 5, "Arab": 9, "Thousand": 3}


def format_price(price: str):
    """
    price is expected to be in format: PKR 1.8 Crore
    """
    parts = price.split(" ")
    print("parts ***==> ", parts)
    if len(parts) != 2:
        return ""
    match = re.search(r"\d+(\.\d+)?", parts[0])
    if match is None:
        print("!!match is None!!")
        return ""
    numeric_part = match.group()
    numeric_value = float(numeric_part)
    numeric_value *= 10 ** mapping[parts[1]]
    return numeric_value


def relative_time_to_timestamp(relative_time):
    now = datetime.now()

    if "second" in relative_time:
        seconds_ago = int(relative_time.split()[0])
        timestamp = now - timedelta(seconds=seconds_ago)
    elif "minute" in relative_time:
        minutes_ago = int(relative_time.split()[0])
        timestamp = now - timedelta(minutes=minutes_ago)
    elif "hour" in relative_time:
        hours_ago = int(relative_time.split()[0])
        timestamp = now - timedelta(hours=hours_ago)
    elif "day" in relative_time:
        days_ago = int(relative_time.split()[0])
        timestamp = now - timedelta(days=days_ago)
    elif "week" in relative_time:
        weeks_ago = int(relative_time.split()[0])
        timestamp = now - timedelta(weeks=weeks_ago)
    elif "month" in relative_time:
        months_ago = int(relative_time.split()[0])
        # Assuming a month has 30 days for simplicity
        timestamp = now - timedelta(days=months_ago * 30)
    else:
        raise ValueError("Unsupported time format")

    return int(timestamp.timestamp())
