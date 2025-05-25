from schemas.graph_state import GraphState
from util.common_config_loader import COMMON_CONFIG


def end_message(state: GraphState) -> GraphState:
    state["response"] = COMMON_CONFIG["default-message"]["end"]
    return state

