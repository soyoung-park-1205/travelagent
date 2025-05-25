from langchain.prompts import ChatPromptTemplate

from util.common_config_loader import COMMON_CONFIG
from schemas.graph_state import GraphState, TravelPlan
from llm.response_schema import get_plan_format, get_simple_format


def build_plane_prompt(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMON_CONFIG["prompt"]["system"]["kind-planner"]),
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
            아래 유저의 질문에 대해 간결하게 답변 해주세요.
            
            사용자 답변:
            {state["user_answer"]}
            """
    return prompt.invoke({"user_prompt": user_prompt})


def get_previous_bot_response(state: GraphState) -> str:
    messages = state["messages"]
    # 가장 최근 bot 메시지 반환
    for message in reversed(messages):
        return message.content

    return ""


def build_plan_format_prompt(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMON_CONFIG["prompt"]["system"]["kind-planner"]),
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
            봇의 이전 답변과 사용자의 답변을 고려하여 여행 계획서를 업데이트 해주세요.
            봇의 이전 답변에 있는 내용은 사용자가 동의한 내용에 대해서만 추가합니다.
            봇의 이전 답변이나 사용자 답변에 없는 값을 억지로 만들어서 추가하지 마세요.
            일정은 년도 값이 없을 경우 기본적으로 2025년 입니다.
            
            봇의 이전 답변:
            {get_previous_bot_response(state)}
            사용자 답변:
            {state["user_answer"]}
            기존 계획서:
            {state["plan"]}
            
            아래 포맷에 맞춰 travel_plan을 JSON 형식으로 생성해주세요.
        {get_plan_format()}
        """
    return prompt.invoke({"user_prompt": user_prompt})


def get_plan_format_only_user_response(state: GraphState) -> GraphState:
    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMON_CONFIG["prompt"]["system"]["kind-planner"]),
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                사용자의 답변만을 고려하여 여행 계획서를 업데이트 해주세요.
                사용자 답변에 없는 값을 억지로 만들어서 추가하지 마세요.
                일정은 년도 값이 없을 경우 기본적으로 2025년 입니다.
                
                사용자 답변:
                {state["user_answer"]}
                기존 계획서:
                {state["plan"]}

                아래 포맷에 맞춰 travel_plan을 JSON 형식으로 생성해주세요.
            {get_plan_format()}
            """
    return prompt.invoke({"user_prompt": user_prompt})


def build_yorn_answer_check_format_prompt(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
            사용자의 답변이 네, 아니요, 좋아요, 싫어요 등 긍/부정에 관련한 답변인지 여부를 y 혹은 n으로 판단해주세요.
            
            사용자 답변:
            {state["user_answer"]}
            {get_simple_format("is_yorn", "")}
            """
    return prompt.invoke({"user_prompt": user_prompt})


def build_detect_question_type_prompt(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
            사용자 질문의 유형을 반드시 아래 4개 중에 하나를 선택하여 부연설명 없이 유형만 리턴해주세요.
            
            [질문 유형]
            1. yorn
            2. about_travel
            3. about_calendar
            4. send_kakaotalk
            5. default
            
            [유형별 설명]
            1. yorn: 답변이 네, 아니요, 좋아요, 싫어요 등 긍/부정에 관련한 답변입니다.
            2. about_travel: 여행지, 여행 일정, 여행 계획, 동행자 등 여행 관련 내용이거나, 계획서 수정/추가를 요청하는 내용입니다.
            3. about_calendar: 캘린더에 조회, 추가, 수정, 삭제 등과 관련된 내용입니다. (캘린더에 작업하는 것만 해당함, 계획서 수정 관련 내용은 아님)
            4. send_kakaotalk: 카카오톡(카톡)을 보내달라는 내용입니다.
            5. default: 위 4가지 유형에 속하지 않는 그 외 내용입니다.

            사용자 답변:
            {state["user_answer"]}
            {get_simple_format("question_type", "질문 타입")}
            """
    return prompt.invoke({"user_prompt": user_prompt})


def build_about_travel_format_prompt(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                사용자의 답변이 여행지, 여행 일정, 여행 계획, 동행자 등 여행 관련 내용인지 여부를 y 혹은 n으로 판단해주세요.
                
                사용자 답변:
                {state["user_answer"]}
                {get_simple_format("is_about_travel", "")}
                """
    return prompt.invoke({"user_prompt": user_prompt})


def build_about_calendar_format_prompt(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                사용자의 답변이 캘린더 관련 내용인지 여부를 y 혹은 n으로 판단해주세요.

                사용자 답변:
                {state["user_answer"]}
                {get_simple_format("is_about_calendar", "")}
                """
    return prompt.invoke({"user_prompt": user_prompt})


def build_user_wants_recommend_response(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                사용자의 답변을 사용자가 현재 여행지 관련 추천을 원하는 상태인지 여부를 y 혹은 n으로 판단해주세요.
                
                봇의 이전 답변:
                {state["response"] if "response" in state else ""}

                사용자 답변:
                {state["user_answer"]}
                {get_simple_format("is_user_wants_recommend", "")}
                """
    return prompt.invoke({"user_prompt": user_prompt})


def build_calendar_job_response(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                사용자는 캘린더 수정을 원하는 상황입니다. 사용자의 답변에서 캘린더에서 어떤 작업을 원하는지 확인하여 리턴해주세요.
                
                [작업 리스트]
                1. add (캘린더에 일정 추가)
                2. show (캘린더 조회)
                3. delete (일정 삭제)
                4. edit (일정 수정)
                
                봇의 이전 답변:
                {state["response"] if "response" in state else ""}

                사용자 답변:
                {state["user_answer"]}
                {get_simple_format("job", "")}
                """
    return prompt.invoke({"user_prompt": user_prompt})


def build_search_result_recom_prompt(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMON_CONFIG["prompt"]["system"]["kind-planner"]),
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                    사용자는 여행 관련 추천을 원하는 상황입니다. 
                    아래의 여행 관련 정보를 활용하여 사용자에게 사용자 질문에 답변해주세요.

                    [조건]
                    1. 사용자의 현재 여행 계획서가 작성되어 있을 경우 참고하여 답변합니다.
                    2. 여행 관련 정보는 참고용이고 사용자 질문에 대한 답변을 해면 됩니다.
                    
                    여행 관련 정보: 
                    {state["contents"]}
                    봇의 이전 답변:
                    {state["response"] if "response" in state else ""}

                    사용자 질문:
                    {state["user_answer"]}
                    
                    여행 계획서:
                    {state["plan"]}
                    
                    """
    return prompt.invoke({"user_prompt": user_prompt})


def build_calendar_job_answer_response(state: GraphState, calendar_job):
    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMON_CONFIG["prompt"]["system"]["kind-planner"]),
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                사용자가 캘린더 {calendar_job} 작업을 요청한 상황입니다.
                작업을 마친후 사용자에게 마무리 멘트를 20자 이내로 간략하게 해주세요.

                사용자 답변:
                {state["user_answer"]}
                """
    return prompt.invoke({"user_prompt": user_prompt})


def build_kakaotalk_send_response(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMON_CONFIG["prompt"]["system"]["kind-planner"]),
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                사용자가 요청한 카카오톡 전송 작업을 마친 상태입니다.
                작업을 마친후 사용자에게 마무리 멘트를 20자 이내로 간략하게 해주세요.

                사용자 답변:
                {state["user_answer"]}
                """
    return prompt.invoke({"user_prompt": user_prompt})


def build_calendar_read_answer_response(state: GraphState, calendar_contents):
    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMON_CONFIG["prompt"]["system"]["kind-planner"]),
        ("human", "{user_prompt}")
    ])
    user_prompt = f"""
                사용자가 캘린더 일정 조회 작업을 요청한 상황입니다.
                캘린더 일정 조회 결과를 안내하는 멘트를 작성해주세요.
                일정 제목과 날짜만(시간은 제외) 간략하게 보여주세요.
                
                캘린더 일정:
                {calendar_contents}

                사용자 답변:
                {state["user_answer"]}
                """
    return prompt.invoke({"user_prompt": user_prompt})