from typing import Annotated

from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

from schemas.travel_plan import TravelPlan

class GraphState(TypedDict):
    user_answer: str
    messages: Annotated[list, add_messages]
    response: str
    contents: str
    thread_id: str
    plan: TravelPlan
