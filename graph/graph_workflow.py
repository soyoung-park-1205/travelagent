import json
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph

from graph.plan_updater import update_plan_from_feedback, update_plan_only_user
from graph.retriever import search_recom_contents
from service.llm_service import get_bot_response
from service.kakaoapi_service import (add_calendar_schedule, show_calendar_schedule,
                                      edit_calendar_schedule, delete_calendar_schedule,
                                      send_kakao_talk)
from data_formatter.travel_plan_factory import default_travel_plan
from message.message_loader import *
from graph.condition_checker import is_user_wants_recommend, find_calendar_job, detect_question_type

memory = MemorySaver()
memory.storage.clear()  # 재시작 시 메모리 초기화


def empty_node(state: GraphState):
    return state


# LangGraph workflow 정의
workflow = StateGraph(state_schema=GraphState)
workflow.add_node("search_recom_contents", search_recom_contents)
workflow.add_node("detect_question_type", detect_question_type)
workflow.add_node("is_user_wants_recommend", empty_node)
workflow.add_node("plane_response", get_bot_response)
workflow.add_node("do_calendar_job", empty_node)
workflow.add_node("add_calendar_schedule", add_calendar_schedule)
workflow.add_node("show_calendar_schedule", show_calendar_schedule)
workflow.add_node("delete_calendar_schedule", delete_calendar_schedule)
workflow.add_node("edit_calendar_schedule", edit_calendar_schedule)
workflow.add_node("send_kakao_talk", send_kakao_talk)

workflow.add_conditional_edges(START,
                               detect_question_type,
                               {
                                   "yorn": "plane_response",
                                   "about_travel": "is_user_wants_recommend",
                                   "about_calendar": "do_calendar_job",
                                   "send_kakaotalk": "send_kakao_talk",
                                   "default": "plane_response"
                               }
                               )
workflow.add_conditional_edges("is_user_wants_recommend",
                               is_user_wants_recommend,
                               {
                                   True: "search_recom_contents",
                                   False: "plane_response"
                               })
workflow.add_conditional_edges("do_calendar_job",
                               find_calendar_job,
                               {
                                   "add": "add_calendar_schedule",
                                   "show": "show_calendar_schedule",
                                   "delete": "delete_calendar_schedule",
                                   "edit": "edit_calendar_schedule"
                               })
workflow.set_finish_point("plane_response")
workflow.set_finish_point("add_calendar_schedule")
workflow.set_finish_point("show_calendar_schedule")
workflow.set_finish_point("delete_calendar_schedule")
workflow.set_finish_point("edit_calendar_schedule")
workflow.set_finish_point("search_recom_contents")
workflow.set_finish_point("send_kakao_talk")

app = workflow.compile(checkpointer=memory)

print(app.get_graph(xray=True).draw_mermaid())


async def get_user_travel_plan(thread_id: str):
    """사용자의 저장된 여행 계획을 가져오는 함수"""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = await app.aget_state(config)

        if state and state.values and "plan" in state.values:
            return state.values["plan"]
        else:
            return default_travel_plan()
    except Exception as e:
        print(f"Error getting travel plan: {e}")
        return default_travel_plan()


async def ask_model(thread_id: str, user_answer: str):
    # MemorySaver에서 기존 여행 계획 가져오기
    saved_plan = await get_user_travel_plan(thread_id)

    # Graph 진입 전에 1차 계획서 업데이트 (메모리 저장은 안함)
    pre_state = {
        "user_answer": user_answer,
        "messages": [],
        "thread_id": thread_id,
        "plan": saved_plan
    }

    # 1차 업데이트 수행 (사용자 답변만을 기반으로, 메모리 저장 X)
    updated_pre_state = update_plan_from_feedback(pre_state)
    updated_plan = updated_pre_state.get("plan")

    plan_data = convert_plan_to_dict(updated_plan)
    yield f"data: {json.dumps({'plan': plan_data})}\n\n"

    input_data = {
        "user_answer": user_answer,
        "messages": [],
        "thread_id": thread_id,
        "plan": updated_plan
    }

    final_state = None
    current_chain_node = None

    # 사용자에 실제 나가는 응답 생성 노드들 (streaming 대상)
    RESPONSE_NODES = [
        "plane_response",
        "search_recom_contents",
        "add_calendar_schedule",
        "show_calendar_schedule",
        "delete_calendar_schedule",
        "edit_calendar_schedule",
        "send_kakao_talk"
    ]

    async for event in app.astream_events(
            input_data,
            {"configurable": {"thread_id": thread_id}},
            stream_mode="values"
    ):
        kind = event["event"]
        node_name = event.get("name", "")

        # 현재 실행 중인 체인 노드 추적
        if kind == "on_chain_start" and node_name in RESPONSE_NODES:
            current_chain_node = node_name

        elif kind == "on_chain_end" and node_name in RESPONSE_NODES:
            current_chain_node = None

        # chat 스트리밍 중 실제 응답만 출력
        elif kind == "on_chat_model_stream" and current_chain_node:
            chunk = event["data"]["chunk"]
            if hasattr(chunk, 'content') and chunk.content:
                yield f"data: {json.dumps({'text': chunk.content})}\n\n"

        # 최종 결과 수집
        elif kind == "on_chain_end" and node_name == "LangGraph":
            final_state = event["data"]["output"]

    # 최종 상태 처리 및 계획 업데이트
    if final_state:
        updated_state = update_plan_from_feedback(final_state)

        # 업데이트된 plan 출력
        final_plan = updated_state.get("plan")

        # 계획을 프론트엔드로 전송
        final_plan_data = convert_plan_to_dict(final_plan)
        yield f"data: {json.dumps({'plan_updated': final_plan_data})}\n\n"

        # memory에 최종 업데이트된 plan 저장
        await save_user_travel_plan(thread_id, final_plan)

    else:
        yield f"data: {json.dumps({'text': COMMON_CONFIG['default-message']['error']})}\n\n"



async def get_all_user_threads():
    try:
        return list(memory.storage.keys()) if hasattr(memory, 'storage') else []
    except Exception as e:
        return []


async def delete_user_travel_plan(thread_id: str):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        await app.aupdate_state(config, {
            "plan": default_travel_plan(),
            "user_answer": "",
            "thread_id": thread_id,
            "response": "",
            "contents": ""
        })
        return True
    except Exception as e:
        print(f"Error deleting travel plan: {e}")
        return False


def convert_plan_to_dict(plan):
    if isinstance(plan, dict):
        return plan

    if hasattr(plan, '__dict__'):
        plan_dict = {}

        # 기본 정보
        if hasattr(plan, 'region'):
            plan_dict['destination'] = plan.region
        if hasattr(plan, 'start_at'):
            plan_dict['start_date'] = plan.start_at
        if hasattr(plan, 'end_at'):
            plan_dict['end_date'] = plan.end_at

        # 일정 정보
        if hasattr(plan, 'schedules') and plan.schedules:
            itinerary = []
            for i, schedule in enumerate(plan.schedules):
                schedule_dict = {
                    'day': f'일정 {i + 1}',
                    'location': getattr(schedule, 'spot', f'일정 {i + 1}'),
                }

                if hasattr(schedule, 'time'):
                    time_obj = schedule["time"]
                    if hasattr(time_obj, 'start_at') and hasattr(time_obj, 'end_at'):
                        schedule_dict['time'] = f"{time_obj['start_at']} - {time_obj['end_at']}"

                itinerary.append(schedule_dict)

            plan_dict['itinerary'] = itinerary

        return plan_dict

    return {}


async def save_user_travel_plan(thread_id: str, updated_plan):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        current_state = await app.aget_state(config)

        if current_state and current_state.values:
            new_state = current_state.values.copy()
            new_state["plan"] = updated_plan
        else:
            new_state = {
                "plan": updated_plan,
                "user_answer": "",
                "messages": [],
                "thread_id": thread_id,
                "response": ""
            }

        await app.aupdate_state(config, new_state)
        return True
    except Exception as e:
        print(f"Error saving travel plan: {e}")
        return False
