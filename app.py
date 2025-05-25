import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from graph.graph_workflow import ask_model

# FastAPI 앱 설정
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/response")
async def get_response(request: dict):
    question = request.get("question", "")
    thread_id = request.get("thread_id", "default_thread")

    async def generate_response():
        try:
            async for chunk in ask_model(thread_id, question):
                yield chunk
        except Exception as e:
            print(f"Error in generate_response: {e}")
            yield f"data: {json.dumps({'text': '오류가 발생했습니다.'})}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
