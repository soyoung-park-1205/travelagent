### Brief Description

1. 여행 계획서를 기억하고 대화를 통해 내용을 업데이트 함
2. 여행 일정을 캘린더에 조회, 수정, 삭제하기 위해 톡캘린더 API를 사용함 ([개발자센터 바로가기](https://developers.kakao.com/docs/latest/ko/talkcalendar/rest-api))
3. 여행 계획서를 외부에 공유하기 위해 카카오톡 API를 사용함 ([개발자센터 바로가기](https://developers.kakao.com/docs/latest/ko/kakaotalk-message/common))
4. 매번 final_state 마다 봇의 이전 답변, 사용자의 질문을 토대로 계획서 업데이트를 수행함
5. 스트리밍 방식으로 제공하기 위해 astream_events를 사용함

### **Key Technologies**

| **Category** | **Details** |
| --- | --- |
| **Languages** | Python, HTML |
| **Frameworks** | Flask, FastAPI |
| **Library** | LangGraph |
| **Model** | GPT4.1 |

### 대화 화면 캡처

전체 프로세스 녹화 영상 URL: https://www.youtube.com/watch?v=iSAcWthP8Tk

1. 인삿말 / 여행지 및 일정 정하기

![Image](https://github.com/user-attachments/assets/abbf8ad1-478e-4c65-90d2-276aea7f306a)

2. 사용자 의사에 따라 계획서 반영

![Image](https://github.com/user-attachments/assets/65401a99-22fb-4df2-b72e-29afc7bf0608)

3. 최근 일정 조회 및 일정 수정 사항 확인

![Image](https://github.com/user-attachments/assets/71766a76-852c-4f81-be46-3bd20a013939)

4. 캘린더 수정, 카카오톡 전송 요청 및 마무리 인사말

![Image](https://github.com/user-attachments/assets/efafc82e-15a6-4a99-85e2-c7c1c64e0c4b)

<table>
  <tr>
    <td align="center">
      <p>캘린더 화면 (As-is)</p>
      <img width="250" src="https://github.com/user-attachments/assets/176d20b8-773c-42b0-8fa3-93895e8dca40" />
    </td>
    <td align="center">
      <p>캘린더 화면 (To-be)</p>
      <img width="250" src="https://github.com/user-attachments/assets/8d7d614f-b54b-4ce8-81ad-785ddb74763a" />
    </td>
    <td align="center">
      <p>카카오톡 전송 화면</p>
      <img width="250" src="https://github.com/user-attachments/assets/db8ec8ef-6e07-4af7-b17f-2eb255eb3161" />
    </td>
  </tr>
</table>


### LangGraph

- 상태 (state) 관리를 위해 **MemorySaver**를 사용함
- **add_messages**를 사용하여 이전 message를 기억할 수 있도록 함

### LangGraph Detail

![Image](https://github.com/user-attachments/assets/f39b19cd-58ee-4dc6-8ca5-31bd4c4e1cdc)

- **node**
    1. `plane_response`
        - 일반적인 답변
    2. `search_recom_contents`
        - 한국관광공사_국문 관광정보 서비스 API를 활용하여 관광 정보 검색후 답변 **(**[GW 정보 바로가기](https://www.data.go.kr/data/15101578/openapi.do)**)**
    3. `add_calendar_schedule`
        - 톡캘린더에 일정 추가
    4. `show_calendar_schedule`
        - 톡캘린더 일정 보여주기
    5. `delete_calendar_schedule`
        - 톡캘린더 일정 삭제
    6. `edit_calendar_schedule`
        - 톡캘린더 일정 수정 (삭제 + 추가)
    7. `send_kakao_talk` 
        - 여행 일정 카카오톡 메시지 전송
- **conditional_edge**
    1. `detect_question_type`: 질문 타입 감지 (분기처리 위함)
        1. 질문 타입 정의
            1. yorn: 네/아니오와 같은 봇의 이전 답변에 대한 긍/부정 → `plane_response` 
            2. about_travel: 여행 관련 → `is_user_wants_recommend`
            3. about_calendar: 캘린더 작업 관련 → `do_calendar_job`
            4. send_kakakotalk: 카카오톡 메시지 전송 요청 → `send_kakao_talk`
            5. default: 그 외 일반 질문 → `plane_response`
    2. `is_user_wants_recommend`: 사용자가 추천을 원하고 있는지 여부
        1. boolean으로 분기 처리
            1. True → `search_recom_contents`
            2. False → `plane_response`
    3. `do_calendar_job`: 캘린더 작업 분기 처리
        1. add: 캘린더 추가 → `add_calendar_schedule`
        2. delete: 캘린더 삭제 → `delete_calendar_schedule`
        3. edit: 캘린더 수정 → `edit_calendar_schedule`
        4. show: 캘린더 조회 → `show_calendar_schedule`

### 실행 방법

1. config/git.yaml 파일을 복제하여 config/local.yaml 파일 생성후 API 각각에 대해 개인 key 입력
2. app.py, chat_demo.py 실행후 localhost:5001에서 챗 데모 페이지 확인 가능

### LLM 가드레일

1. (전체) System 프롬프트 설정
    - 역할: 여행 플래너로서 계획성이 돋보이는 답변 제공
    - 프롬프트
        
        당신은 국내 여행의 일정과 목표 관리를 돕는 조언자로 정확한 계획성이 돋보이는 말투를 사용합니다.
        
2. (전체) Response 가드레일
    - 역할: 원하는 포맷으로 받아서 활용
    - 각 프롬프트에 `ResponseSchema`를 활용하여 응답 포맷을 명시함
3. 계획서 업데이트 프롬프트 
    - 공통 조건
        - 임의의 값을 생성하지 않도록 명시
        - 날짜에 연도가 누락될 경우 2025년으로 고정
    - (봇 답변 기반)
        - 사용자의 동의 없이 업데이트하지 않도록 명시
    - (사용자 답변 기반)
        - 사용자 답변만을 고려하도록 명시
4. 요청한 캘린더 작업 판단 프롬프트
    - 사용자의 입력을 기반으로 아래 4가지 작업 중 하나로 분류
        1. add - 캘린더에 일정 추가
        2. show - 캘린더 조회
        3. delete - 일정 삭제
        4. edit - 일정 수정
5. 질문 타입 감지 프롬프트
    - 사용자의 질문을 아래 5가지 중 하나로 분류
        1. yorn - 답변이 네, 아니요, 좋아요, 싫어요 등 긍/부정에 관련한 답변
        2. about_travel - 여행지, 여행 일정, 여행 계획, 동행자 등 여행 관련 내용이거나, 계획서 수정/추가를 요청하는 내용
        3. about_calendar - 캘린더에 조회, 추가, 수정, 삭제 등과 관련된 내용
        4. send_kakaotalk - 카카오톡(카톡)을 보내달라는 내용
        5. default - 위 4가지 유형에 속하지 않는 그 외 내용
6. 여행 관련 내용 추천 답변 프롬프트
    - 아래 조건에 따라 응답 수행
        
        1. 사용자의 현재 여행 계획서가 작성되어 있을 경우 참고하여 답변
        
        2. 여행 관련 정보는 참고용이고 사용자 질문에 대해 답변
        
- 그 외 답변 포맷에 대해 글자수, 답변 스타일 등을 각각 명시함

### 장애 대응 방안

1. **LLM 모델 장애 대응 방안**
    - ✅ 방안 1) 현재 모델인 GPT 모델 장애시 Claude API로 우회하여 서비스
        - 장점: GPT 장애시 대응 가능
        - 단점:
            1. GPT, Claude 동시 장애시 같은 이슈 발생
            2. LLM Model이 교체되어 일관된 사용자 경험에 방해가 됨 
            → 프롬프트를 별도로 테스트, 관리하여 해결 가능
    - ✅ 방안 2) 사내 자체 LLM 모델로 우회하여 서비스
        - 장점: GPT API 장애시 대응 가능
        - 단점:
            1. 사내 리소스 추가 사용으로 인한 비용 발생, 추가 협업 필요
            2. 자체 LLM 모델을 구축 및 서비스해야 하므로 기술적 복잡도가 늘어남
            3. 유료 API에 비해 성능이 떨어질 수 있음
2. **캘린더 / 카카오톡 전송 API 장애 대응 방안**
    - ✅ 방안 1) 메시지 큐로 관리하여 사용자에게 안내 후 추후에 API 응답 정상화시 작업 수행
        - 장점: 사용자 만족도 증가
        - 단점: 메시지 큐와 API 정상 응답 여부를 주기적으로 체크해야함 (→ 리소스 사용 증가)
3. **관광 API 장애 대응 방안**
    - ✅ 방안 1) 주기적으로 서비스 지역별 관광 정보 API 응답 결과를 문서로 내려 관리함
        - 장점: 관광 API 장애시 유사한 내용을 서비스 할 수 있음
        - 단점: 문서를 따로 관리해야하고 node가 늘어남
    - ✅ 방안 2) 검색 API로 우회하여 서비스
        - 장점: 관광 API 장애시 실시간 검색 내용을 제공할 수 있음
        - 단점: 비정형 데이터로 품질에 대한 보장이 어려움

### 참고 사항

1. thread_id는 1로 고정하였습니다.
2. 카카오톡 전송 기능은 현재 나에게 보내기만 가능합니다.

### 품질 고도화 / 개선 방안

1. 동행자 데이터 추가 및 동행자 카카오톡 전송 기능 추가 (테스트앱에서만 나에게 보내기만 가능하여 제외함)
2. Prompt 관리 및 고도화를 위한 프롬프트 관리기 작업 / 프롬프트별 모델 & 파라미터 다양화 방안 구축
3. 현재는 검색 기반 추천시에만 (node: `search_recom_contents`) 답변을 기억함, 
추후에 유의미한 정보를 판별하여 해당 정보만 저장하도록 수정
