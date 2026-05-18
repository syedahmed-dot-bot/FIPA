import os
from click import prompt
from dotenv import load_dotenv


from anthropic import Anthropic

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from typer import prompt


load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma")

COLLECTION_MAP = {
    "drilling": "drilling_docs",
    "refinery": "refinery_docs",
    "guidelines": "guidelines_docs"
}

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model_name = os.getenv("MODEL_NAME")

def run_query_pipeline(domain: str, keyword: str, prompt: str) -> dict:
    collection_name = COLLECTION_MAP.get(domain)
    if not collection_name:
        raise ValueError(f"Unsupported domain: {domain}")

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

    query = f"{keyword} {prompt}"
    results_with_scores = vectorstore.similarity_search_with_score(query, k=5)
    retrieved_chunks = [doc.page_content for doc, score in results_with_scores]
        
    guidelines_store = Chroma(
        collection_name=COLLECTION_MAP["guidelines"],
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
    guidelines_chunks = [doc.page_content for doc in guidelines_store.similarity_search(prompt, k=2)]

    chunks_text = "\n\n".join(retrieved_chunks)
    guidelines_text = "\n\n".join(guidelines_chunks)

    final_prompt = f"""
    Equipment: {keyword}
    Engineer Issue: {prompt}

    Relevant Equipment Documentation:
    {chunks_text}

    Safety Guidelines:
    {guidelines_text}

    Provide a precise diagnostic response including:
    - Root cause analysis
    - Step by step corrective actions aligned with safety guidelines
    - Part replacement recommendation with part number if applicable
    - Inventory and procurement details if replacement is needed
    Format as numbered steps. Be concise.
    """

    response = client.messages.create(
        model=model_name,
        max_tokens=1000,
        temperature=0.3,
        system="You are an expert diagnostic assistant for oil and gas field engineers. Be concise and precise.",
        messages=[{"role": "user", "content": final_prompt}]
    )
    response_text = response.content[0].text.strip()

    procurement_needed = any(
        word in response_text.lower() 
        for word in ["replace", "replacement", "part number", "order", "procurement"]
    )
    confidence_prompt = f"""
    On a scale of 0 to 100, how confident are you that your response accurately answers this query based on the provided documentation?

    Query: {prompt if 'prompt' in locals() else query}
    Response summary: {response_text[:200]}

    Reply with ONLY a number between 0 and 100. Nothing else.
    """

    confidence_response = client.messages.create(
        model=model_name,
        max_tokens=10,
        temperature=0.0,
        messages=[{"role": "user", "content": confidence_prompt}]
    )

    try:
        confidence = float(confidence_response.content[0].text.strip())
        confidence = max(0.0, min(100.0, confidence))
    except:
        confidence = 50.0

    return {
        "response": response_text,
        "confidence": confidence,
        "procurement_needed": procurement_needed,
        "sources": retrieved_chunks
    }