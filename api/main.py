from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.core import query_search, generate_response, create_llm_prompt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    text: str
    url: str

class LLMResponse(BaseModel):
    answer: str
    links: List[Link]


@app.post("/generate-answer", response_model=LLMResponse)
def generate_answer(request: QueryRequest):
    try:
        query = request.question
        discourse_context, course_context = query_search(query)
        prompt = create_llm_prompt(query, discourse_context, course_context, request.image)
        result = generate_response(prompt)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e) or "Unknown server error")


