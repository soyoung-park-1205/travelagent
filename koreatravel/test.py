import requests

from util.status_config_loader import CONFIG

url = "https://kapi.kakao.com/v2/api/calendar/events"

headers = {
    "Authorization": f"Bearer {CONFIG['kakao-oauth']['soyoung']}"  # 사용자 access token
}

params = {
    "from": "2022-10-26T00:00:00Z",
    "to": "2022-10-30T00:00:00Z",
    "limit": 2
}

response = requests.get(url, headers=headers, params=params)

print("Status:", response.status_code)

try:
    print("Response:", response.json())
except Exception:
    print("Raw:", response.text)
