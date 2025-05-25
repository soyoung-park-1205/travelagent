from schemas.graph_state import GraphState
from kakaoapi.calendar import *
from kakaoapi.kakao_talk import *
from llm.llm_answer import get_calendar_add_ment_response, get_calendar_read_ment_response, get_kakaotalk_send_response


def add_calendar_schedule(state: GraphState):
    create_schedule(state["plan"])
    state["response"] = get_calendar_add_ment_response(state, "추가")
    return state


def show_calendar_schedule(state: GraphState):
    calendar_contents = get_recent_schedule_contents()
    state["response"] = get_calendar_read_ment_response(state, calendar_contents)
    return state

def delete_calendar_schedule(state: GraphState):
    delete_schedule(state["plan"])
    state["response"] = get_calendar_add_ment_response(state, "삭제")
    return state

def edit_calendar_schedule(state: GraphState):
    update_schedule(state["plan"])
    state["response"] = get_calendar_add_ment_response(state, "수정")
    return state

def send_kakao_talk(state: GraphState):
    send_calendar_kakaotalk(state["plan"])
    state["response"] = get_kakaotalk_send_response(state)
    print("kakao talk response: ", state["response"])

    return state

