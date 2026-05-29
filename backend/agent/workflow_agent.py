import os

from dotenv import load_dotenv


from langgraph.graph import StateGraph, END, START
from anthropic import Anthropic

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from typing import TypedDict, Annotated

import operator

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma")

COLLECTION_MAP = {
    "drilling": "drilling_docs",
    "refinery": "refinery_docs"
}

CACHE_DIR = os.path.join(BASE_DIR, "data", "embeddings_cache")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=CACHE_DIR
)
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model_name = os.getenv("MODEL_NAME")
ollama_model = os.getenv("OLLAMA_MODEL")


class WorkflowState(TypedDict):
    domain: str                                         #drilling or refinery
    keyword: str                                        #equipment keyword from the engineer
    retrieved_chunks: Annotated[list, operator.add]     #chunks from Chroma
    failure_modes: Annotated[list, operator.add]        #extracted failure modes from chunks
    prompts: list                                       #final 5 prompts replaced


def retrieve_chunks(state: WorkflowState) -> dict:
    collection_name = COLLECTION_MAP.get(state["domain"])
    if not collection_name:
        raise ValueError(f"Unsupported domain: {state['domain']}")
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
    
    query = state["keyword"]
    results = vectorstore.similarity_search(query, k=5)
    return {"retrieved_chunks": [doc.page_content for doc in results]}

def extract_failure_modes(state: WorkflowState) -> dict:
    chunks_text = "\n\n".join(state["retrieved_chunks"])
    
    prompt = f"""
    Given the following technical document chunks, extract all failure modes related to {state['keyword']}.

    {chunks_text}

    List each failure mode on a new line. Be concise. Include error codes where available.
    """
    
    response = client.messages.create(
        model=model_name,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    failure_modes = response.content[0].text.strip().split("\n")

    return {"failure_modes": [f for f in failure_modes if f.strip()]}

def generate_prompts(state: WorkflowState) -> dict:
    failure_modes_text = "\n".join(state["failure_modes"])
    
    prompt = f"""
    Based on these failure modes for {state['keyword']}:

    {failure_modes_text}

    Generate exactly 5 failure mode statements ranked by severity — most critical first.
    Each statement should describe a specific problem the engineer is experiencing.
    Write from the engineer's perspective — what they are observing, not what you are asking them.
    Format: one statement per line, no numbering, no bullet points.

    Examples of correct format:
    - Pump losing prime with sudden loss of discharge pressure
    - Relief valve drifting above setpoint during operation
    - Excessive vibration detected in bearing assembly

    Examples of WRONG format:
    - Have you checked the relief valve?
    - What is the current pressure reading?
    """

    response = client.messages.create(
        model=model_name,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    prompts = [
        line.strip() 
        for line in response.content[0].text.strip().split("\n") 
        if line.strip()
    ][:5]
    
    return {"prompts": prompts}

workflow = StateGraph(WorkflowState)

workflow.add_node("retrieve", retrieve_chunks)
workflow.add_node("extract", extract_failure_modes)
workflow.add_node("generate", generate_prompts)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "extract")
workflow.add_edge("extract", "generate")
workflow.add_edge("generate", END)

workflow_graph = workflow.compile()

def run_workflow_agent(domain: str, keyword: str) -> list:
    result = workflow_graph.invoke({
        "domain": domain,
        "keyword": keyword,
        "retrieved_chunks": [],
        "failure_modes": [],
        "prompts": []
    })
    return result["prompts"]

