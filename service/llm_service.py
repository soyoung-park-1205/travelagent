from schemas.graph_state import GraphState
from llm.llm_answer import get_plane_response

def get_bot_response(state: GraphState) -> GraphState:
    state["response"] = get_plane_response(state)
    return state
