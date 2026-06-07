import os

from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from anthropic import Anthropic
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data", "embeddings_cache")

COLLECTION_MAP = {
    "drilling": "drilling-docs",
    "refinery": "refinery-docs",
    "guidelines": "guidelines-docs"
}


CACHE_DIR = os.path.join(BASE_DIR, "data", "embeddings_cache")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=CACHE_DIR
)


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model_name = os.getenv("MODEL_NAME")
index_name = os.getenv("PINECONE_INDEX")


system_prompt = """You are an expert diagnostic assistant for oil and gas field engineers. Be concise and precise.
If the prompt is just a single keyword, ask the user to provide more details about the issue they are facing.
For example, if the user inputs 'pump', respond with a request for more details about the specific issue."""


def run_chat_agent(message: str, domain: str, conversation_history: list) -> dict:
    collection_name = COLLECTION_MAP.get(domain)
    if not collection_name:
        raise ValueError(f"Unsupported domain: {domain}")

    vectorstore = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=collection_name
    )

    results_with_scores = vectorstore.similarity_search_with_score(message, k=5)
    retrieved_chunks = [doc.page_content for doc, score in results_with_scores]

    guidelines_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=COLLECTION_MAP["guidelines"]
    )
    guidelines_chunks = [doc.page_content for doc in guidelines_store.similarity_search(message, k=2)]

    chunks_text = "\n\n".join(retrieved_chunks)
    guidelines_text = "\n\n".join(guidelines_chunks)

    prompt = f"""Domain: {domain}
    Engineer Query: {message}

    Relevant Equipment Documentation:
    {chunks_text}

    Relevant Safety Guidelines:
    {guidelines_text}

    Provide a precise diagnostic response including:
    - Root cause of the issue
    - Step by step corrective actions
    - Safety compliance notes
    - Part replacement recommendation if applicable
    Format as numbered steps. Maximum 500 tokens."""

    response = client.messages.create(
        model=model_name,
        max_tokens=1000,
        temperature=0.5,
        system=system_prompt,
        messages=conversation_history + [{"role": "user", "content": prompt}]
    )
    response_text = response.content[0].text.strip()
    procurement_needed = any(
            word in response_text.lower()
            for word in ["replace", "replacement", "part number", "order", "procurement"]
        )
    
    try:

        confidence_prompt = f"""
        You are evaluating a technical diagnostic response for oil and gas equipment.
        Score from 0 to 10 how well this response addresses the engineer's query.
        - 9-10: Complete answer with specific steps, part numbers, safety notes
        - 6-8: Partial answer, missing some details
        - 3-5: Vague answer, lacks specifics
        - 0-2: Does not address the query

        Query: {prompt}
        Response: {response_text[:300]}

        Reply with ONLY a number. Nothing else.
        """
        confidence_response = client.messages.create(
            model=model_name,
            max_tokens=10,
            temperature=0.0,
            messages=[{"role": "user", "content": confidence_prompt}]
        )
        confidence = float(confidence_response.content[0].text.strip())
        confidence = max(0.0, min(10.0, confidence))
    except:
        confidence = 5.0

    return {
        "response": response_text,
        "procurement_needed": procurement_needed,
        "confidence": confidence,
        "sources": retrieved_chunks
    }
