from llm.llm_answer import *


def detect_question_type(state: GraphState) -> str:
    question_type = get_detect_question_type_response(state)
    print(question_type)
    return question_type["question_type"]


def is_user_wants_recommend(state: GraphState) -> bool:
    user_wants_recommend = get_user_wants_recommend_response(state)
    return True if user_wants_recommend["is_user_wants_recommend"] == "y" else False


def find_calendar_job(state: GraphState) -> str:
    calendar_job = get_calendar_job_response(state)
    return calendar_job["job"]
