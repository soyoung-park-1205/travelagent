from schemas.travel_plan import TravelPlan


def default_travel_plan():
    return TravelPlan(region="", start_at="", end_at="", schedules=[])
