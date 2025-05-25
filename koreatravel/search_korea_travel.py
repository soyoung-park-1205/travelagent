import random

import requests

from util.status_config_loader import CONFIG
from util.common_config_loader import COMMON_CONFIG

from schemas.graph_state import GraphState

def get_travel_search_result(state: GraphState) -> str:
    try:
       return get_region_spots(state['plan'].region)
    except:
        return get_region_spots(state['plan']['region'])


def get_region_spots(region: str) -> str:
    if region == "":# 지역이 없을 경우 랜덤
        region = random.choice(list(COMMON_CONFIG['korea-travel']['area-code'].keys()))
    area_code_config = COMMON_CONFIG['korea-travel']['area-code']
    if region not in area_code_config:
        return ""
    area_code = area_code_config[region]
    url = (f"{CONFIG['api-url']['korea-travel']['area-spot']}?"
           f"serviceKey={CONFIG['api-auth']['korea-travel']['auth-key']}"
           f"&MobileOS=WEB&MobileApp=Test&areaCode={area_code}"
           f"&contentTypeId=12&arrange=Q&numOfRows=40&_type=json")
    response = requests.get(url)
    if response.status_code == 200:
        spots = f"{region}의 여행지 리스트: "
        response = response.json()
        items = response['response']['body']['items']['item']
        for item in items:
            spots += item['title'] + " "
        return spots

    return ""

