from schemas.graph_state import GraphState
from llm.llm_answer import get_plan_format_response, get_plan_format_only_user_response


def update_plan_from_feedback(state: GraphState) -> GraphState:
    state["plan"] = get_plan_format_response(state)
    return state


def update_plan_only_user(state: GraphState) -> GraphState:
    """사용자 답변만을 기반으로 업데이트"""
    state["plan"] = get_plan_format_only_user_response(state)
    return state
