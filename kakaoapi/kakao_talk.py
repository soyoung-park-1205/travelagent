import requests
import json

from schemas.travel_plan import TravelPlan

from util.status_config_loader import CONFIG
from util.common_config_loader import COMMON_CONFIG


def send_calendar_kakaotalk(plan: TravelPlan):
    try:
        url = CONFIG['api-url']['kakaotalk']['send']
        soyoung_oauth_code = CONFIG['kakao-oauth']['soyoung']
        schedule_str = ""
        try:
            for schedule in plan["schedules"]:
                schedule_str += f"{schedule['spot']} ->"
        except Exception as e:
            print(e)
        data_dict = {
            "template_id": COMMON_CONFIG['kakaotalk']['msg-template-id'],
            "template_args": json.dumps({
                "user": "박소영",
                "region": plan['region'],
                "start_at": plan['start_at'],
                "end_at": plan['end_at'],
                "schedule_str": schedule_str
            })
        }
        response = requests.post(
            url,
            data=data_dict,
            headers={
                "Authorization": f"Bearer {soyoung_oauth_code}",
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
            }
        )
        if response.status_code != 200 or response.json()['result_code'] != 0:
            return False
        return True
    except Exception as e:
        print("HTTP Error ", e)
        return False
