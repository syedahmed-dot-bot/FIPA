from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import traceback

from agent.workflow_agent import run_workflow_agent
from agent.query import run_query_pipeline
from agent.chat_agent import run_chat_agent

load_dotenv()

app = FastAPI(title="FIPA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GeneratePromptsRequest(BaseModel):
    domain: str
    keyword: str

class GeneratePromptsResponse(BaseModel):
    prompts: list

class QueryRequest(BaseModel):
    domain: str
    keyword: str
    prompt: str

class QueryResponse(BaseModel):
    response: str
    confidence: float
    procurement_needed: bool

class ChatRequest(BaseModel):
    message: str
    domain: str
    conversation_history: list

class ChatResponse(BaseModel):
    response: str
    confidence: float

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/generate-prompts", response_model=GeneratePromptsResponse)
def generate_prompts(request: GeneratePromptsRequest):
    try:
        prompts = run_workflow_agent(request.domain, request.keyword)
        return GeneratePromptsResponse(prompts=prompts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        result = run_query_pipeline(request.domain, request.keyword, request.prompt)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = run_chat_agent(request.message, request.domain, request.conversation_history)
        return ChatResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))