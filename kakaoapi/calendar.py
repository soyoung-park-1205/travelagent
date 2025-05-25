import json
import requests
from schemas.travel_plan import TravelPlan

from util.status_config_loader import CONFIG


def read_schedule():
    try:
        url = f"{CONFIG['api-url']['calendar']['watch']}"
        soyoung_oauth_code = CONFIG['kakao-oauth']['soyoung']
        params = {
            "from": "2025-05-01T00:00:00Z",
            "to": "2025-06-01T00:00:00Z"
        }
        response = requests.get(url,
                     headers={
                         "Authorization": f"Bearer {soyoung_oauth_code}",
                         "Content-Type": "application/x-www-form-urlencoded"
                     },
                    params=params
                     )
        events = response.json()['events']
        return events
    except Exception as e:
        print("HTTP Error:", e)
        return []

def get_recent_schedule_contents():
    events = read_schedule()
    events_str = ""
    for event in events:
        if "title" in event:
            events_str += f"{event['title']} : {event['time']['start_at']} ~ {event['time']['end_at']}\n"
    return events_str


def create_schedule(plan):
    try:
        url = f"{CONFIG['api-url']['calendar']['create']}?filter=USER"
        soyoung_oauth_code = CONFIG['kakao-oauth']['soyoung']
        data_dict = {
            "calendar_id": "primary",
            "event": json.dumps({
                "title": plan['region'] + " 여행",
                "time": {
                    "start_at": plan['start_at'],
                    "end_at": plan['end_at'] if 'end_at' in plan else plan['start_at'],
                    "time_zone": "Asia/Seoul",
                    "all_day": False,
                    "lunar": False
                },
                "description": "일정 설명"
            })
        }
        response = requests.post(
            url,
            data=data_dict,
            headers={
                "Authorization": f"Bearer {soyoung_oauth_code}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        if response.status_code != 200:
            return False
        return True
    except Exception as e:
        print("HTTP Error:", e)
        return False


def delete_schedule(plan):
    try:
        events = read_schedule()
        target_id = ""
        for event in events:
            if "title" in event:
                if event['title'] == f"{plan.region} 여행":
                    target_id = event['id']
        url = f"{CONFIG['api-url']['calendar']['delete']}"
        if target_id == "":
            return False
        soyoung_oauth_code = CONFIG['kakao-oauth']['soyoung']
        params = {
            "event_id": target_id
        }
        response = requests.delete(url,
                                headers={
                                    "Authorization": f"Bearer {soyoung_oauth_code}",
                                    "Content-Type": "application/x-www-form-urlencoded"
                                },
                                params=params
                                )
        if response.status_code != 200:
            return False
        return True
    except Exception as e:
        print("HTTP Error:", e)
        return False


def update_schedule(plan: TravelPlan):
    if delete_schedule(plan['region']) is False:
        return False
    if create_schedule(plan) is False:
        return False
    return True
