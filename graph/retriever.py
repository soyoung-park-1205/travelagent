from schemas.graph_state import GraphState

from koreatravel.search_korea_travel import get_travel_search_result
from llm.llm_answer import get_travel_recom_ment_response

def search_recom_contents(state: GraphState) -> GraphState:
    state["contents"] = get_travel_search_result(state)
    state["response"] = get_travel_recom_ment_response(state)
    state["messages"] = [state["response"]]
    return state
