from langchain.output_parsers import StructuredOutputParser, ResponseSchema


def get_plan_format():
    response_schemas = [
        ResponseSchema(name="region", description="여행 지역"),
        ResponseSchema(name="start_at", description="여행 시작 시간 (yyyy-MM-dd 포맷)"),
        ResponseSchema(name="end_at", description="여행 완료 시간  (yyyy-MM-dd 포맷)"),
        ResponseSchema(name="schedules", description="""
            일정 리스트.
            각 항목의 구조는 아래와 같습니다. 값이 있을 때만 채워주세요.
            {
              "spot": "장소",
              "time": {
                "start_at": "ISO8601 형식 시작 시간",
                "end_at": "ISO8601 형식 종료 시간",
                "time_zone": "Asia/Seoul"
              }
            }
            """)
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return output_parser.get_format_instructions()


def get_simple_format(key, description):
    response_schemas = [
        ResponseSchema(name=key, description=description)
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return output_parser.get_format_instructions()
