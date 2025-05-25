import os
import certifi
import json
from util.common_config_loader import COMMON_CONFIG

from langchain_openai import ChatOpenAI

from util import status_config_loader
from llm.prompt import *

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["OPENAI_API_KEY"] = status_config_loader.CONFIG["api-auth"]["gpt"]["key"]

llm = ChatOpenAI(
    api_key=status_config_loader.CONFIG["api-auth"]["gpt"]["key"],
    model=COMMON_CONFIG['gpt']['model'],
    streaming=True,
    temperature=1
)

def get_llm_answer(prompt, type="json"):
    state = llm.invoke(prompt, config={"configurable": {"thread_id": "1"}})
    content = state.content
    if type == "json":
        return json.loads(content[content.index('{'): content.rindex('}') + 1])
    else:
        return content


def get_plane_response(state: GraphState):
    prompt = build_plane_prompt(state)
    return get_llm_answer(prompt, "str")


def get_plan_format_response(state: GraphState):
    prompt = build_plan_format_prompt(state)
    return get_llm_answer(prompt)


def get_plan_format_only_user_response(state: GraphState):
    prompt = get_plan_format_only_user_response(state)
    return get_llm_answer(prompt)


def get_detect_question_type_response(state: GraphState):
    prompt = build_detect_question_type_prompt(state)
    return get_llm_answer(prompt)

def get_yorn_response(state: GraphState):
    prompt = build_yorn_answer_check_format_prompt(state)
    return get_llm_answer(prompt)


def get_about_travel_response(state: GraphState):
    prompt = build_about_travel_format_prompt(state)
    return get_llm_answer(prompt)


def get_about_calendar_response(state: GraphState):
    prompt = build_about_calendar_format_prompt(state)
    return get_llm_answer(prompt)


def get_user_wants_recommend_response(state: GraphState):
    prompt = build_user_wants_recommend_response(state)
    return get_llm_answer(prompt)


def get_calendar_job_response(state: GraphState):
    prompt = build_calendar_job_response(state)
    return get_llm_answer(prompt)


def get_travel_recom_ment_response(state: GraphState):
    prompt = build_search_result_recom_prompt(state)
    return get_llm_answer(prompt, "str")


def get_calendar_add_ment_response(state: GraphState, job: str):
    prompt = build_calendar_job_answer_response(state, job)
    return get_llm_answer(prompt, "str")


def get_kakaotalk_send_response(state: GraphState):
    prompt = build_kakaotalk_send_response(state)
    return get_llm_answer(prompt, "str")


def get_calendar_read_ment_response(state: GraphState, calendar_contents: str):
    prompt = build_calendar_read_answer_response(state, calendar_contents)
    return get_llm_answer(prompt, "str")
