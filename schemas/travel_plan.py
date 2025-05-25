from pydantic.dataclasses import dataclass


@dataclass
class Time:
    start_at: str
    end_at: str


@dataclass
class Schedule:
    spot: str
    time: Time


@dataclass
class TravelPlan:
    region: str
    start_at: str
    end_at: str
    schedules: list[Schedule]
